import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CookieState } from '../abstractions/states';
import { MatchResponse } from '../abstractions/messages';

export default function JoinMatchPage() {
  const [searchParams] = useSearchParams()
  const [cookie, setCookie] = useCookies(['shengji'])
  const [cookieState, setCookieState] = useState(new CookieState());
  const [match, setMatch] = useState(parseInt(searchParams.get("match_id") ?? "-1"));
  const navigate = useNavigate()

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setCookieState({
      name: savedOptions?.['name'] || "",
      debug: savedOptions?.['debug'] || false
    });
  }, [cookie])

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.value;
    setCookieState(values => ({...values, [name]: value}));
  }

  const handleMatchChange = (event: React.ChangeEvent<HTMLInputElement>) =>
    setMatch(parseInt(event.target.value));

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', cookieState, { path: '/'})
    const response = await fetch(`${process.env.REACT_APP_API_URL || ''}/match/${match}`);
    const matchResponse = new MatchResponse(await response.text());
    navigate(`/${matchResponse.id}`, { state: { name: cookieState.name, matchResponse: matchResponse } });
  }

  return (
    <div className="container">
      <CookiesProvider>
        <h1>Join a match</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Player name</label>
          <input
            autoFocus
            id="name"
            type="text"
            name="name"
            placeholder="Name"
            value={cookieState.name || ""}
            onChange={handleNameChange}
            required
          />
          <label htmlFor="match">Match</label>
          <input
            id="match"
            type="number"
            name="match"
            placeholder="Match"
            value={match >= 0 ? match : undefined}
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
