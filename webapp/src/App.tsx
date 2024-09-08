import { BrowserRouter, Routes, Route } from "react-router-dom";
import Chat from "./pages/Chat";
import Home from "./pages/Home";
import NewMatch from './pages/NewMatch';
import Match from './pages/Match';
import JoinMatch from './pages/JoinMatch';

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<Home />} />
          <Route path="chat" element={<Chat />} />
          <Route path="/:id" element={<Match />} />
          <Route path="newMatch" element={<NewMatch />} />
          <Route path="joinMatch" element={<JoinMatch />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;