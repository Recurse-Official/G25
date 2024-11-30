import React, { useEffect } from "react";
import Logo from "../assets/logo.svg";
import { FaGithub } from "react-icons/fa";
import { LogOutIcon, LucideLogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

const NavButton = ({ children, variant = 'ghost', onClick }) => {
  const baseStyle = "px-4 py-2 rounded-lg font-medium transition-colors duration-200";
  const styles = {
    ghost: "hover:bg-gray-100 text-gray-700",
    primary: "bg-[#24292f] text-white hover:bg-[#31373d] flex items-center gap-2 py-2.5 px-5 text-[16px] rounded-md",
    outline: "border border-gray-300 hover:bg-gray-50",
    danger: "bg-red-500 text-white hover:bg-red-600"
  };

  return (
    <button
      className={`${variant === 'primary' ? styles.primary : `${baseStyle} ${styles[variant]}`}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

const Navigation = ({ isLoggedIn, setIsLoggedIn, setIsLoading }) => {

  const GITHUB_CLIENT_ID = import.meta.env.VITE_GITHUB_CLIENT_ID;
  const GITHUB_REDIRECT_URI = import.meta.env.VITE_GITHUB_REDIRECT_URI;

  const userToken = localStorage.getItem('tokenInfo');
  const userData = localStorage.getItem('userInfo');

  const navigate = useNavigate();

  useEffect(() => {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const codeParam = urlParams.get('code');

    const fetchAuthData = async () => {
      try {
        if (codeParam && !isLoggedIn) {
          setIsLoading(true);
          const tokenResponse = await fetch(`http://localhost:8000/api/auth/access-token?code=${codeParam}`);
          if (!tokenResponse.ok) {
            console.error('Failed to fetch access token:', tokenResponse);
            throw new Error('Failed to fetch access token');
          }
          const tokenData = await tokenResponse.json();
          localStorage.setItem('tokenInfo', JSON.stringify(tokenData));

          const userResponse = await fetch('http://localhost:8000/api/auth/user-data', {
            headers: {
              'Authorization': `Bearer ${tokenData.access_token}`,
              'Accept': 'application/json'
            }
          });
          if (!userResponse.ok) {
            console.error('Failed to fetch user data:', userResponse);

            throw new Error('Failed to fetch user data');
          }
          const userData = await userResponse.json();
          localStorage.setItem('userInfo', JSON.stringify(userData));

          setIsLoggedIn(true);
          setIsLoading(false);
          window.history.replaceState({}, document.title, window.location.pathname);
        }
      } catch (error) {
        console.error('Authentication error:', error);
        localStorage.removeItem('tokenInfo');
        localStorage.removeItem('userInfo');
        setIsLoggedIn(false);
      }
    };

    if (codeParam) {
      fetchAuthData();
    }

  }, []);

  const handleLogin = async () => {
    try {

      const githubOAuthURL = new URL('https://github.com/login/oauth/authorize');
      githubOAuthURL.searchParams.append('client_id', GITHUB_CLIENT_ID);
      githubOAuthURL.searchParams.append('redirect_uri', GITHUB_REDIRECT_URI);
      githubOAuthURL.searchParams.append('scope', 'repo admin:repo_hook read:user');
      githubOAuthURL.searchParams.append('prompt', 'consent');
      githubOAuthURL.searchParams.append('login', '');

      window.location.href = githubOAuthURL.toString();

    } catch (error) {
      console.error("Error during login:", error);
      throw new Error("Failed to initialize GitHub OAuth flow");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('tokenInfo');
    localStorage.removeItem('userInfo');
    setIsLoggedIn(false);
    navigate('/');
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm">
      <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-28 py-2">
        <div className="flex items-center justify-between h-16 relative">

          <div className="flex items-center">
            <Link to="/">
              <img src={Logo} alt="Doccie" className="h-14 w-auto" />
            </Link>
          </div>

          {isLoggedIn ? (
            <div className="flex gap-2 items-center">
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg ">
                <img
                  src={JSON.parse(userData).avatar_url}
                  alt="User Avatar"
                  className="h-8 w-8 rounded-full"
                />
                <span>{JSON.parse(userData).name}</span>

              </div>

              <div
                className="flex items-center rounded-full w-8 h-8 justify-center bg-gray-100 cursor-pointer"
                onClick={handleLogout}
                title="Logout"
              >
                <LogOutIcon className="w-4 h-4 text-gray-500" />
              </div>
            </div>
          ) : (
            <div className="flex items-center">
              <NavButton variant="primary" onClick={handleLogin}>
                <FaGithub size={20} className="text-white" />
                <span>Log in with Github</span>
              </NavButton>
            </div>
          )
          }
        </div>
      </div>
    </nav>
  );
};

export default Navigation;