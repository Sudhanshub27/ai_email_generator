"use client";

import dynamic from "next/dynamic";
import { SpotlightHover } from "@/components/ui/spotlight-hover";

const Spline = dynamic(
  () => import("@splinetool/react-spline"),
  { ssr: false, loading: () => null }
);

export function SplineSceneBasic() {
  return (
    <div className="relative w-full h-full bg-[#0b0f1a] overflow-hidden">
      
      {/* Ambient glow */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[420px] h-[420px] rounded-full bg-indigo-500/10 blur-[120px]" />
      </div>

      {/* Hover spotlight */}
      <SpotlightHover className="bg-white/10" size={260} />

      {/* Spline (lazy + no SSR) */}
      <Spline
        scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
        className="w-full h-full relative z-10"
      />
    </div>
  );
}
