"use client";

import { useEffect, useState, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import parseGeoraster from "georaster";
import GeoRasterLayer from "georaster-layer-for-leaflet";

interface NodeData {
  name: string;
  longitude: number;
  latitude: number;
  uuid: string;
  status: string;
  data: Record<string, number>;
}

export default function NetworkUpdates() {
  const [updates, setUpdates] = useState<NodeData[]>([]);
  const mapRef = useRef<L.Map | null>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [tiffFile, setTiffFile] = useState<File | null>(null);
  const markersRef = useRef<L.LayerGroup>(L.layerGroup());
  const [mapLoaded, setMapLoaded] = useState(false);

  // Load default TIFF map
  useEffect(() => {
    const loadDefaultMap = async () => {
      try {
        const response = await fetch('/maps/default_map.tif', { mode: 'cors' });
        const arrayBuffer = await response.arrayBuffer();
        const georaster = await parseGeoraster(arrayBuffer);
    
        if (mapContainerRef.current && !mapRef.current) {
          const map = L.map(mapContainerRef.current).setView(
            [38.541, -121.774], 15
          );
          mapRef.current = map;
    
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
    
          layer.addTo(map);
          markersRef.current.addTo(map);
          setMapLoaded(true);
        }
      } catch (error) {
        console.error("Error loading default map:", error);
        setMapLoaded(false);
      }
    };
    

    loadDefaultMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  // Handle user file upload
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setTiffFile(file);

      try {
        const arrayBuffer = await file.arrayBuffer();
        const georaster = await parseGeoraster(arrayBuffer);
        
        if (mapRef.current) {
          // Clear existing layers except markers
          mapRef.current.eachLayer(layer => {
            if (layer !== markersRef.current) {
              mapRef.current?.removeLayer(layer);
            }
          });

          // Add new raster layer
          const layer = new GeoRasterLayer({
            georaster: georaster,
            opacity: 0.8,
            pixelValuesToColorFn: values => {
              const value = values[0];
              const intensity = Math.min(255, Math.max(0, value));
              return `rgb(${intensity}, ${intensity}, ${intensity})`;
            },
            resolution: 256
          });
          layer.addTo(mapRef.current);
          setMapLoaded(true);
        }
      } catch (error) {
        console.error("Error loading uploaded map:", error);
        setMapLoaded(false);
      }
    }
  };

  // WebSocket connection for updates
  useEffect(() => {
    const ws = new WebSocket("ws://localhost:7654");

    ws.onopen = () => console.log("Connected to WebSocket server");

    ws.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        if (!update.node?.longitude || !update.node?.latitude) return;

        setUpdates((prevUpdates) => [update.node, ...prevUpdates]);

        if (mapRef.current) {
          const marker = L.circleMarker(
            [update.node.latitude, update.node.longitude],
            {
              radius: 8,
              fillColor: update.node.status === "Active" ? "blue" : "red",
              color: "#fff",
              weight: 1,
              opacity: 1,
              fillOpacity: 0.8
            }
          ).bindPopup(`
            <b>${update.node.name}</b><br>
            UUID: ${update.node.uuid}<br>
            Status: ${update.node.status}<br>
            Data: ${JSON.stringify(update.node.data)}
          `);

          markersRef.current.addLayer(marker);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const terminateServer = async () => {
    if (window.confirm("Are you sure you want to shut down the server?")) {
      try {
        const response = await fetch("http://localhost:5002/shutdown", {
          method: "POST",
        });
        const result = await response.text();
        console.log(result);
        alert("Server shutting down...");
      } catch (error) {
        console.error("Error shutting down the server:", error);
        alert("Failed to shut down the server.");
      }
    }
  };

  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: "20px",
      width: "100%",
      minHeight: "100vh",
      backgroundColor: "#d0e7ff",
      padding: "20px",
    }}>
      <h1 style={{ color: "#000", fontWeight: "bold", fontSize: "3rem" }}>Network Dashboard</h1>

      {/* File input for custom TIFF */}
      <div style={{ width: "100%", maxWidth: "600px" }}>
        <label style={{ display: "block", marginBottom: "10px" }}>
          Upload Custom GeoTIFF Map (optional):
        </label>
        <input
          type="file"
          accept=".tif,.tiff"
          onChange={handleFileChange}
          style={{ width: "100%" }}
        />
      </div>

      {/* Map container */}
      <div
        ref={mapContainerRef}
        style={{
          height: "400px",
          width: "100%",
          maxWidth: "800px",
          border: "2px solid white",
          backgroundColor: "#f0f0f0",
        }}
      >
        {!mapLoaded && (
          <div style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            color: "#666",
          }}>
            Loading map...
          </div>
        )}
      </div>

      <button
        onClick={terminateServer}
        style={{
          marginTop: "10px",
          padding: "12px 24px",
          backgroundColor: "red",
          color: "white",
          border: "2px solid white",
          cursor: "pointer",
          fontWeight: "bold",
        }}
      >
        Terminate Server
      </button>

      <h2 style={{ color: "#000", fontWeight: "bold", textTransform: "uppercase", fontSize: "2rem" }}>
        Node Updates
      </h2>

      <div style={{
        width: "90%",
        maxWidth: "600px",
        display: "flex",
        flexDirection: "column",
        gap: "5px",
      }}>
        {updates.map((node, index) => (
          <div
            key={index}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "10px",
              border: "2px solid white",
              backgroundColor: "white",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div
                style={{
                  width: "15px",
                  height: "15px",
                  backgroundColor: node.status === "Active" ? "blue" : "red",
                }}
              ></div>
              <strong style={{ color: "black" }}>{node.name}</strong>
            </div>
            <div style={{ fontSize: "0.9em", color: "#555" }}>
              <span>UUID: {node.uuid}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}