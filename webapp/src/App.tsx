import { BrowserRouter, Routes, Route } from "react-router-dom";
import MatchChatPage from "./pages/MatchChatPage";
import HomePage from "./pages/HomePage";
import NewMatchPage from './pages/NewMatchPage';
import MatchPage from './pages/MatchPage';
import JoinMatchPage from './pages/JoinMatchPage';

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/">
          <Route index element={<HomePage />} />
          <Route path="chat" element={<MatchChatPage />} />
          <Route path="/:id" element={<MatchPage />} />
          <Route path="newMatch" element={<NewMatchPage />} />
          <Route path="joinMatch" element={<JoinMatchPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;