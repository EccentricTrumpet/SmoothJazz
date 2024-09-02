import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<Socket>();

  // Establish socket connection
  useEffect(() => {
    console.log('establishing connection')

    const newSocket = io("localhost:5000/", {
      transports: ["websocket"],
    })

    newSocket.on("connect", () => {
      setSocket(newSocket)
      console.log('socket connected');
    });

    newSocket.on("disconnect", () => {
      console.log('socket disconnected');
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  // Receive messages
  useEffect(() => {
    if (socket) {
      socket.on("data", (data) => {
        setMessages(prevMessages => [...prevMessages, data.data]);
      });
      console.log('data event started')

      return () => {
        socket.off("data", () => {
          console.log("data event stopped");
        });
      };
    }
  }, [socket]);

  // UI handlers
  const handleText = (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputMessage = e.target.value;
    setMessage(inputMessage);
  };
  const handleSubmit = () => {
    if (socket) {
      socket.emit("data", message);
      setMessage("");
    }
  };

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
    <div>
      <h2>WebSocket Communication</h2>
      <input type="text" value={message} onChange={handleText} />
      <button onClick={handleSubmit}>submit</button>
      <ul>
        {messages.map((message, ind) => {
          return <li key={ind}>{message}</li>;
        })}
      </ul>
    </div>
  ));
}
