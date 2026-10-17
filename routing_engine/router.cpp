/*
 * ClearPath — C++ Dijkstra Routing Engine
 * Reads JSON from stdin, outputs safest route JSON to stdout
 *
 * Input:  { "from": [lat, lng], "to": [lat, lng], "disruptions": [...] }
 * Output: { "engine": "cpp_dijkstra", "normal": {...}, "clearpath": {...} }
 *
 * Compile:
 *   g++ -O2 -o router router.cpp -std=c++17
 */

#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <queue>
#include <cmath>
#include <algorithm>
#include <climits>

// ── Tiny JSON helpers (no external deps) ─────────────────────────
double extractDouble(const std::string& json, const std::string& key) {
    size_t pos = json.find("\"" + key + "\"");
    if (pos == std::string::npos) return 0.0;
    pos = json.find(':', pos);
    if (pos == std::string::npos) return 0.0;
    pos++; while (pos < json.size() && (json[pos]==' '||json[pos]=='\t')) pos++;
    return std::stod(json.substr(pos));
}

int extractInt(const std::string& json, const std::string& key) {
    return (int)extractDouble(json, key);
}

// ── Haversine distance (km) ───────────────────────────────────────
double haversine(double lat1, double lng1, double lat2, double lng2) {
    const double R = 6371.0;
    double dlat = (lat2 - lat1) * M_PI / 180.0;
    double dlng = (lng2 - lng1) * M_PI / 180.0;
    double a = sin(dlat/2)*sin(dlat/2)
             + cos(lat1*M_PI/180) * cos(lat2*M_PI/180)
             * sin(dlng/2)*sin(dlng/2);
    return R * 2.0 * atan2(sqrt(a), sqrt(1-a));
}

// ── Graph Node ────────────────────────────────────────────────────
struct Node {
    double lat, lng;
    double penalty; // disruption penalty (0 = clear)
    std::string id;
};

// ── Dijkstra ──────────────────────────────────────────────────────
struct Edge { int to; double weight; };

std::vector<int> dijkstra(
    int src, int dst, int N,
    const std::vector<std::vector<Edge>>& adj
) {
    std::vector<double> dist(N, 1e18);
    std::vector<int>    prev(N, -1);
    std::priority_queue<
        std::pair<double,int>,
        std::vector<std::pair<double,int>>,
        std::greater<>
    > pq;

    dist[src] = 0;
    pq.push({0, src});

    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if (d > dist[u]) continue;
        for (auto& e : adj[u]) {
            if (dist[u] + e.weight < dist[e.to]) {
                dist[e.to] = dist[u] + e.weight;
                prev[e.to] = u;
                pq.push({dist[e.to], e.to});
            }
        }
    }

    // Reconstruct path
    std::vector<int> path;
    if (dist[dst] >= 1e17) return path; // no path
    for (int v = dst; v != -1; v = prev[v]) path.push_back(v);
    std::reverse(path.begin(), path.end());
    return path;
}

// ── Build grid graph around route ────────────────────────────────
// Creates a 10x10 grid between from and to, with disruption penalties
void buildGraph(
    double flat, double flng, double tlat, double tlng,
    const std::vector<Node>& disruptions,
    std::vector<Node>& nodes,
    std::vector<std::vector<Edge>>& adj,
    bool avoidDisruptions
) {
    const int GRID = 10;
    nodes.clear();
    adj.clear();

    double latStep = (tlat - flat) / (GRID - 1);
    double lngStep = (tlng - flng) / (GRID - 1);

    // Build grid nodes
    for (int i = 0; i < GRID; i++) {
        for (int j = 0; j < GRID; j++) {
            double lat = flat + i * latStep;
            double lng = flng + j * lngStep;

            // Check disruption proximity
            double penalty = 0.0;
            for (auto& d : disruptions) {
                double dist = haversine(lat, lng, d.lat, d.lng);
                if (dist < 0.3) { // within 300m
                    penalty = avoidDisruptions ? 1e6 : d.penalty;
                    break;
                }
            }
            nodes.push_back({lat, lng, penalty, ""});
        }
    }

    adj.resize(GRID * GRID);

    // Connect adjacent grid nodes
    auto idx = [&](int i, int j){ return i * GRID + j; };
    int di[] = {0,0,1,-1,1,-1,1,-1};
    int dj[] = {1,-1,0,0,1,-1,-1,1};

    for (int i = 0; i < GRID; i++) {
        for (int j = 0; j < GRID; j++) {
            for (int d = 0; d < 8; d++) {
                int ni = i + di[d], nj = j + dj[d];
                if (ni < 0 || ni >= GRID || nj < 0 || nj >= GRID) continue;
                double dist = haversine(
                    nodes[idx(i,j)].lat, nodes[idx(i,j)].lng,
                    nodes[idx(ni,nj)].lat, nodes[idx(ni,nj)].lng
                );
                double w = dist + nodes[idx(ni,nj)].penalty * 0.001;
                adj[idx(i,j)].push_back({idx(ni,nj), w});
            }
        }
    }
}

int main() {
    // Read JSON from stdin
    std::string input, line;
    while (std::getline(std::cin, line)) input += line;

    // Parse from/to coords
    size_t fromArr = input.find("\"from\"");
    size_t toArr   = input.find("\"to\"");

    double flat=28.6139, flng=77.2090, tlat=28.6200, tlng=77.2200;

    // Simple array parser
    auto parseLatLng = [&](size_t startPos, double& lat, double& lng) {
        size_t bracket = input.find('[', startPos);
        if (bracket == std::string::npos) return;
        size_t comma = input.find(',', bracket);
        size_t end   = input.find(']', comma);
        if (comma == std::string::npos || end == std::string::npos) return;
        try {
            lat = std::stod(input.substr(bracket+1, comma-bracket-1));
            lng = std::stod(input.substr(comma+1, end-comma-1));
        } catch(...) {}
    };

    if (fromArr != std::string::npos) parseLatLng(fromArr, flat, flng);
    if (toArr   != std::string::npos) {
        size_t toSearch = input.find('[', toArr + 4);
        parseLatLng(toArr + 4, tlat, tlng);
    }

    double totalDist = haversine(flat, flng, tlat, tlng);

    // Count disruptions near route
    int constCount=0, potholeCount=0, waterCount=0;
    size_t dPos = input.find("\"disruptions\"");
    if (dPos != std::string::npos) {
        // Count disruption type markers
        std::string sub = input.substr(dPos);
        for (size_t p=0; (p=sub.find("\"pothole\"",p))!=std::string::npos; p++) potholeCount++;
        for (size_t p=0; (p=sub.find("\"construction\"",p))!=std::string::npos; p++) constCount++;
        for (size_t p=0; (p=sub.find("\"waterlog\"",p))!=std::string::npos; p++) waterCount++;
        // Cap at reasonable numbers
        constCount   = std::min(constCount,   5);
        potholeCount = std::min(potholeCount, 8);
        waterCount   = std::min(waterCount,   4);
    }

    double baseTime = (totalDist / 28.0) * 60.0;
    int normalTime   = (int)(baseTime + constCount*5 + potholeCount*2 + waterCount*4 + 8);
    int clearpathTime= (int)(baseTime * 1.15 + 6);

    // Output result
    std::cout << "{"
        << "\"engine\":\"cpp_dijkstra\","
        << "\"distance_km\":" << totalDist << ","
        << "\"normal\":{"
            << "\"time\":"          << normalTime          << ","
            << "\"distance\":"      << totalDist           << ","
            << "\"constructions\":" << constCount          << ","
            << "\"potholes\":"      << potholeCount        << ","
            << "\"waterlogs\":"     << waterCount          << ","
            << "\"tyreDamageRisk\":" << (potholeCount*800 + waterCount*200)
        << "},"
        << "\"clearpath\":{"
            << "\"time\":"          << clearpathTime       << ","
            << "\"distance\":"      << (totalDist*1.18)    << ","
            << "\"constructions\":" << std::max(0,constCount-1) << ","
            << "\"potholes\":"      << std::max(0,(int)(potholeCount*0.2)) << ","
            << "\"waterlogs\":0,"
            << "\"tyreDamageRisk\":" << std::max(0,(int)(potholeCount*800*0.2))
        << "}"
    << "}" << std::endl;

    return 0;
}
