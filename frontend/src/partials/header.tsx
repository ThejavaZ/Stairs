import Navbar from "./navbar";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <>
      <header className="bg-blue-950 p-5 flex justify-around items-center text-white">
        <Link to="/">
          <img src="/logo.png" alt="logo" className="w-30" />
        </Link>
        <Navbar />
      </header>
    </>
  );
};

export default Header;
