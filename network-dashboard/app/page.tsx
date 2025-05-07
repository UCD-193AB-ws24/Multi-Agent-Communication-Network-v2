"use client";

import dynamic from "next/dynamic";

// Import the NetworkUpdates component without SSR
const NetworkUpdates = dynamic(() => import("../NetworkUpdates"), {
  ssr: false,
});

export default function Home() {
  return (
    <div>
      <NetworkUpdates />
    </div>
  );
}
