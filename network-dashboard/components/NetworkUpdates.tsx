"use client";

import { useEffect, useState, useRef } from "react";
import MapView from "@arcgis/core/views/MapView";
import WebMap from "@arcgis/core/WebMap";
import Graphic from "@arcgis/core/Graphic";
import GraphicsLayer from "@arcgis/core/layers/GraphicsLayer";
import Point from "@arcgis/core/geometry/Point";
import SimpleMarkerSymbol from "@arcgis/core/symbols/SimpleMarkerSymbol";

export default function NetworkUpdates() {
  const [updates, setUpdates] = useState<any[]>([]);
  const mapRef = useRef<HTMLDivElement>(null);
  const graphicsLayerRef = useRef<GraphicsLayer | null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:7654");

    ws.onopen = () => console.log("Connected to WebSocket server");

    ws.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        setUpdates((prevUpdates) => [update, ...prevUpdates]);

        if (graphicsLayerRef.current && update.node?.longitude && update.node?.latitude) {
          const point = new Point({
            longitude: update.node.longitude,
            latitude: update.node.latitude,
          });

          const markerSymbol = new SimpleMarkerSymbol({
            color: "blue",
            outline: { color: "white", width: 1 },
          });

          const pointGraphic = new Graphic({
            geometry: point,
            symbol: markerSymbol,
            attributes: update.node,
            popupTemplate: {
              title: `{name}`,
              content: `UUID: {uuid}<br>Status: {status}<br>Data: {data}`,
            },
          });

          graphicsLayerRef.current.add(pointGraphic);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };

    ws.onclose = () => console.log("Disconnected from WebSocket server");
    ws.onerror = (error) => console.error("WebSocket error:", error);

    return () => ws.close();
  }, []);

  useEffect(() => {
    if (!mapRef.current) return;

    const webMap = new WebMap({ basemap: "streets-navigation-vector" });
    const view = new MapView({
      container: mapRef.current,
      map: webMap,
      center: [-121.774, 38.541], // Center in Davis, CA
      zoom: 15,
    });

    const graphicsLayer = new GraphicsLayer();
    webMap.add(graphicsLayer);
    graphicsLayerRef.current = graphicsLayer;
  }, []);

  // Function to send a request to terminate the Python server
  const terminateServer = async () => {
    if (window.confirm("Are you sure you want to shut down the server?")) {
      try {
        const response = await fetch("http://localhost:5000/shutdown", {
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
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <h1>Network Dashboard</h1>
      <div
        ref={mapRef}
        style={{
          height: "400px",
          width: "100%",
          maxHeight: "100%",
          border: "1px solid #ccc",
          borderRadius: "8px",
          overflow: "hidden",
        }}
      ></div>
      <button
        onClick={terminateServer}
        style={{
          marginTop: "10px",
          padding: "10px 20px",
          backgroundColor: "red",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        Terminate Server
      </button>
    </div>
  );
}
