import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { useNavigate } from 'react-router-dom';
import { CookieState } from '../abstractions/states';
import { MatchResponse } from '../abstractions/messages';

export default function JoinMatchPage() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [cookieState, setCookieState] = useState(new CookieState());
  const [match, setMatch] = useState(-1);
  const navigate = useNavigate()

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setCookieState({
      name: savedOptions?.['name'] || "",
      debug: savedOptions?.['debug'] || false
    });
  }, [cookie])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.value;
    setCookieState(values => ({...values, [name]: value}));
  }

  const handleMatchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setMatch(parseInt(event.target.value));
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', cookieState, { path: '/'})
    const name = cookieState.name
    const response = await fetch(`http://localhost:5001/match/${match}`);
    const matchResponse = new MatchResponse(await response.text());
    navigate(`/${matchResponse.matchId}`, { state: { name: name, matchResponse: matchResponse } });
  }

  return (
    <div className="container">
      <CookiesProvider>
        <h1>Join a match</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Player name</label>
          <input
            id="name"
            type="text"
            name="name"
            placeholder="Name"
            value={cookieState.name || ""}
            onChange={handleChange}
            required
          />
          <label htmlFor="match">Match</label>
          <input
            id="match"
            type="number"
            name="match"
            placeholder="Match"
            onChange={handleMatchChange}
            required
          />

          <button type="submit">
            Join
          </button>
        </form>
      </CookiesProvider>
    </div>
  );
}
