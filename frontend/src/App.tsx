import { Routes, Route } from "react-router-dom";

import Header from "./partials/header";
import Footer from "./partials/footer";

import Home from "./views/home";
function App() {
  return (
    <section className="flex flex-col min-w-full">
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </main>
      <Footer />
    </section>
  );
}

export default App;
