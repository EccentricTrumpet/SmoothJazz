import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { useNavigate } from 'react-router-dom';
import { CookieState } from '../abstractions/states';

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

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', cookieState, { path: '/'})
    navigate(`/${match}`, { state: { name: cookieState.name } });
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
