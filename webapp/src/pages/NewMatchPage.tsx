import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie'
import { useNavigate } from 'react-router-dom';
import { CookieState } from '../abstractions/states';
import { MatchResponse } from '../abstractions/messages';

export default function NewMatchPage() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [cookieState, setCookieState] = useState(new CookieState());
  const navigate = useNavigate()

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setCookieState(new CookieState(
      savedOptions?.['name'],
      JSON.parse(savedOptions?.['debug'] || false)
    ));
  }, [cookie])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setCookieState(values => ({...values, [name]: value}));
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', cookieState, { path: '/'});
    const name = cookieState.name
    const response = await fetch('http://localhost:5001/match', {
      method: 'POST',
      headers:new Headers({
        'Content-type': 'application/json'
      }),
      body: JSON.stringify(cookieState)
    });
    const matchResponse = new MatchResponse(await response.text());
    navigate(`/${matchResponse.matchId}`, { state: { name: name, matchResponse: matchResponse } });
  }

  return (
    <div className="container">
      <CookiesProvider>
        <h1>Create a new match</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Player name</label>
          <input
            id="name"
            type="text"
            name="name"
            placeholder="Name"
            value={cookieState.name}
            onChange={handleChange}
            required
          />
          <details>
            <summary>Settings</summary>
            <fieldset>
              <label htmlFor="debug">
                <input
                  type="checkbox"
                  role="switch"
                  id="debug"
                  name="debug"
                  checked={cookieState.debug || false}
                  onChange={handleChange}
                />
                Debug mode
              </label>
            </fieldset>
          </details>
          <button type="submit">
            Start
          </button>
        </form>
      </CookiesProvider>
    </div>
  );
}
