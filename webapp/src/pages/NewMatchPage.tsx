import { useEffect, useState } from 'react';
import { CookiesProvider, useCookies } from 'react-cookie';
import { useNavigate } from 'react-router-dom';
import { MatchResponse } from '../abstractions/messages';
import { CookieState } from '../abstractions/states';

export default function NewMatchPage() {
  const [cookie, setCookie] = useCookies(['shengji'])
  const [cookieState, setCookieState] = useState(new CookieState());
  const navigate = useNavigate()

  useEffect(() => {
    const savedOptions = cookie['shengji'];
    setCookieState(new CookieState(savedOptions));
  }, [cookie])

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const name = event.target.name;
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setCookieState(values => ({...values, [name]: value}));
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCookie('shengji', cookieState, { path: '/'});
    const response = await (await fetch(`${process.env.REACT_APP_API_URL || ''}/match`, {
      method: 'POST',
      headers: new Headers({ 'Content-type': 'application/json' }),
      body: JSON.stringify(cookieState)
    })).text();
    navigate(`/${new MatchResponse(response).id}`, { state: { name: cookieState.name, match: response } });
  }

  return (
    <div className="container">
      <CookiesProvider>
        <h1>Create a new match</h1>
        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Player name</label>
          <input
            autoFocus
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
                  checked={cookieState.debug}
                  onChange={handleChange}
                />
                Debug mode
              </label>
              <label htmlFor="debug">
                <input
                  type="checkbox"
                  role="switch"
                  id="logs"
                  name="logs"
                  checked={cookieState.logs}
                  onChange={handleChange}
                />
                Game logs
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
