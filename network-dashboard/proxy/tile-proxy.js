const express = require("express");
const axios = require("axios");
const app = express();
const port = 8081;

const BASE_URL = "https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer";

app.get("/tiles/*", async (req, res) => {
  const targetPath = req.params[0];
  const esriUrl = `${BASE_URL}/${targetPath}`;

  try {
    const response = await axios.get(esriUrl, {
      responseType: "arraybuffer",
    });

    const contentType = response.headers["content-type"] || "application/octet-stream";
    res.set("Content-Type", contentType);
    res.send(response.data);
  } catch (err) {
    console.error("Proxy error:", err.message);
    res.status(500).send("Tile fetch failed");
  }
});

app.listen(port, () => {
  console.log(`✅ Tile proxy running at http://localhost:${port}/tiles/...`);
});
