import { useEffect, useState } from "react"

function isMobileDevice() {
  return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    || window.innerWidth < 768
}

export default function App() {
  const [Component, setComponent] = useState(null)

  useEffect(() => {
    if (isMobileDevice()) {
      import("./apps/mobile/MobileApp.jsx").then(m => setComponent(() => m.default))
    } else {
      import("./apps/desktop/DesktopApp.jsx").then(m => setComponent(() => m.default))
    }
  }, [])

  if (!Component) return (
    <div style={{
      height: "100vh", background: "#0c0c0e",
      display: "flex", alignItems: "center", justifyContent: "center",
      color: "#e8e8e6", fontFamily: "system-ui", fontSize: "14px"
    }}>
      Starting Zeno...
    </div>
  )

  return <Component />
}
