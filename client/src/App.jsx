import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Onboarding from "./pages/Onboarding";
import Room from "./pages/Room";
import Hub from "./pages/Hub";
import Roadmap from "./pages/Roadmap";
import Quests from "./pages/Quests";
import FriendRoll from "./pages/FriendRoll";

export default function App() {
  const pages = {
    "/": Landing,
    "/auth": Signup,
    "/signup": Signup,
    "/login": Login,
    "/onboarding": Onboarding,
    "/room": Room,
    "/hub": Hub,
    "/roadmap": Roadmap,
    "/quests": Quests,
    "/friend": FriendRoll,
  };
  const Page = pages[window.location.pathname] || Landing;
  return <Page />;
}
