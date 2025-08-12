const Home = () => {
  return (
    <>
      <section className="flex">
        <article>
          <h1>Zona de grafica principal</h1>

          <canvas>
            <p>Grafica</p>
          </canvas>
          <ul>
            <li>Empleados</li>
            <li>Faltas</li>
          </ul>
        </article>

        <article>
          <ul>
            <li>
              <h2>Turno 1</h2>
            </li>
            <li>
              <h2>Turno 2</h2>
            </li>
            <li>
              <h2>Turno 3 </h2>
            </li>
          </ul>
        </article>
      </section>
    </>
  );
};

export default Home;
