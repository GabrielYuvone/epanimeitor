"use client";

import dynamic from "next/dynamic";

const AnimationEditor = dynamic(
  () => import("@/components/animation/AnimationEditor"),
  { ssr: false }
);

export default function Home() {
  return <AnimationEditor />;
}
