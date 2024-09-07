import { useEffect, useState } from "react";
import { Manager, Socket } from "socket.io-client";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<Socket>();

  // Establish socket connection
  useEffect(() => {
    console.log('establishing connection')

    const manager = new Manager("localhost:5001")
    const chatSocket = manager.socket("/chat")

    chatSocket.on("connect", () => {
      setSocket(chatSocket)
      console.log('socket connected');
    });

    chatSocket.on("disconnect", () => {
      console.log('socket disconnected');
    });

    return () => {
      chatSocket.disconnect();
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
