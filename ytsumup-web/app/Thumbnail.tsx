"use client";
import { state } from "./state";
import YoutubeTitle from "./YoutubeTitle";
import { Suspense } from "react";
import Image from "next/image";

import { snapshot, useSnapshot } from "valtio";

export default function Thumbnail(props: any) {
  const snap = useSnapshot(state);

  if (snap.ytid == "") {
    return (
      <div>
        <Image
          src={snap.thumbnailUrl}
          width="1000"
          height="500"
          alt="Youtube Thumbnail"
          className="  border-solid border-4 border-[#222222] font-sans"
        />
        <h1>{state.ytid}</h1>
      </div>
    );
  } else {
    return (
      <div>
        <img
          src={snap.thumbnailUrl}
          alt=""
          className="h-96  border-solid border-4 border-[#222222] font-sans"
        />
        <Suspense fallback={<p>Loading...</p>}>
          <YoutubeTitle id={state.ytid} />
        </Suspense>
      </div>
    );
  }
}
