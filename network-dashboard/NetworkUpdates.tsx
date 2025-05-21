"use client";

import { useEffect, useState, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import parseGeoraster from "georaster";
import GeoRasterLayer from "georaster-layer-for-leaflet";
import "./style.scss";

interface NodeData {
  name: string;
  longitude: number;
  latitude: number;
  uuid: string;
  status: string;
  data: Record<string, any>;
}

export default function NetworkUpdates() {
  const [updates, setUpdates] = useState<NodeData[]>([]);
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<L.LayerGroup>(L.layerGroup());
  const [mapLoaded, setMapLoaded] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      try {
        const arrayBuffer = await file.arrayBuffer();
        const georaster = await parseGeoraster(arrayBuffer);
        if (mapRef.current) {
          mapRef.current.eachLayer(layer => {
            if (layer !== markersRef.current) mapRef.current.removeLayer(layer);
          });
          const layer = new GeoRasterLayer({
            georaster,
            opacity: 0.8,
            pixelValuesToColorFn: values => {
              const value = values[0];
              const intensity = Math.min(255, Math.max(0, value));
              return `rgb(${intensity}, ${intensity}, ${intensity})`;
            },
            resolution: 256
          });
          layer.addTo(mapRef.current);
        }
      } catch (err) {
        console.error("Error loading uploaded map:", err);
      }
    }
  };

  useEffect(() => {
    const interBubble = document.querySelector<HTMLDivElement>(".interactive");
    if (!interBubble) return;
    let curX = 0, curY = 0, tgX = 0, tgY = 0;
    function move() {
      curX += (tgX - curX) / 20;
      curY += (tgY - curY) / 20;
      interBubble.style.transform = `translate(${Math.round(curX)}px, ${Math.round(curY)}px)`;
      requestAnimationFrame(move);
    }
    window.addEventListener("mousemove", e => {
      tgX = e.clientX;
      tgY = e.clientY;
    });
    move();
    return () => window.removeEventListener("mousemove", () => {});
  }, []);

  useEffect(() => {
    const loadMap = async () => {
      try {
        const response = await fetch("/maps/default_map.tif", { mode: "cors" });
        const arrayBuffer = await response.arrayBuffer();
        const georaster = await parseGeoraster(arrayBuffer);

        if (mapContainerRef.current && !mapRef.current) {
          const map = L.map(mapContainerRef.current).setView([38.5415, -121.775], 15);
          mapRef.current = map;

          const rasterLayer = new GeoRasterLayer({
            georaster,
            opacity: 0.8,
            pixelValuesToColorFn: values => {
              const value = values[0];
              const intensity = Math.min(255, Math.max(0, value));
              return `rgb(${intensity}, ${intensity}, ${intensity})`;
            },
            resolution: 256
          });
          rasterLayer.addTo(map);

          markersRef.current.addTo(map);
          setMapLoaded(true);
        }
      } catch (err) {
        console.error("Error loading default map:", err);
      }
    };
    loadMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:7654");

    ws.onopen = () => {
      console.log("[WebSocket] Connected");
    };

    ws.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);

        if (update.nodes && Array.isArray(update.nodes)) {
          update.nodes.forEach((node: any) => {
            const hasGPS = node.gps?.lat != null && node.gps?.lon != null;

            const mappedNode: NodeData = {
              name: `Node ${node.address}`,
              latitude: hasGPS ? node.gps.lat : 0,
              longitude: hasGPS ? node.gps.lon : 0,
              uuid: node.uuid,
              status: node.status,
              data: node.data || {},
            };

            setUpdates(prev => [mappedNode, ...prev]);

            if (mapRef.current && hasGPS) {
              const marker = L.circleMarker([mappedNode.latitude, mappedNode.longitude], {
                radius: 8,
                fillColor: mappedNode.status === "Active" ? "blue" : "red",
                color: "#fff",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
              }).bindPopup(`
                <b>${mappedNode.name}</b><br>
                UUID: ${mappedNode.uuid}<br>
                Status: ${mappedNode.status}<br>
                Data: ${JSON.stringify(mappedNode.data)}
              `);
              markersRef.current.addLayer(marker);
            }
          });
        }
      } catch (err) {
        console.error("[WebSocket] Error parsing message:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("[WebSocket] Connection error:", err);
    };

    return () => ws.close();
  }, []);

  const terminateServer = async () => {
    if (window.confirm("Are you sure you want to shut down the server?")) {
      try {
        const res = await fetch("http://localhost:5002/shutdown", { method: "POST" });
        const text = await res.text();
        alert("Server shutting down\n" + text);
      } catch {
        alert("Failed to shut down the server.");
      }
    }
  };

  return (
    <div className="gradient-bg">
      <svg>
        <filter id="goo">
          <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
          <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 20 -10" result="goo" />
          <feBlend in="SourceGraphic" in2="goo" />
        </filter>
      </svg>
      <div className="gradients-container">
        <div className="g1"></div>
        <div className="g2"></div>
        <div className="g3"></div>
        <div className="g4"></div>
        <div className="g5"></div>
        <div className="interactive"></div>
      </div>

      <div className="ui-wrapper with-sidebar-offset">
        <div className="sidebar">
          <label htmlFor="file-upload" className="sidebar-button">Upload .tif map</label>
          <input id="file-upload" type="file" accept=".tif,.tiff" onChange={handleFileChange} style={{ display: "none" }} />
          <button className="sidebar-button" onClick={terminateServer}>Terminate Server</button>
        </div>

        <h1 className="dashboard-title with-sidebar-offset">Network Dashboard</h1>

        <div className="dashboard-content">
          <div className="updates-column">
            <h2 className="section-title">Node Updates</h2>
            {updates.map((node, index) => (
              <div key={index} className="node-card">
                <strong>{node.name}</strong><br />
                UUID: {node.uuid}<br />
                Status: {node.status}
              </div>
            ))}
          </div>

          <div ref={mapContainerRef} className="map-container leaflet-container">
            {!mapLoaded && <div className="map-loading">Loading map...</div>}
          </div>
        </div>
      </div>
    </div>
  );
}
