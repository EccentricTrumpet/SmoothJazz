import './App.css';
import WebSocketCall from "./components/WebSocketCall";
import { io, Socket } from "socket.io-client";
import { useEffect, useState } from "react";

function App() {
  const [socketInstance, setSocket] = useState<Socket|null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const socket = io("localhost:5000/", {
      transports: ["websocket"],
    });

    setSocket(socket);

    socket.on("connect", () => {
      console.log('socket connected');
    });

    socket.on("disconnect", (data) => {
      console.log('socket disconnected');
    });

    setLoading(false);

    return function cleanup() {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="App">
      <h1>React/Flask App + socket.io</h1>
      <>
        <div className="line">
          {!loading && <WebSocketCall socket={socketInstance} />}
        </div>
      </>
    </div>
  );
}

export default App;