import { PieChart } from "@mui/x-charts";

type Turn = {
  name: string;
  employees: number;
  fouls: number;
  style: string;
};

export const Turn = ({ name, employees, fouls, style }: Turn) => {
  return (
    <>
      <div className={style}>
        <h1 className="font-black text-2xl">{name}</h1>
        <PieChart
          series={[
            {
              data: [
                { value: employees, label: "Employees" },
                { value: fouls, label: "Fouls" },
              ],
            },
          ]}
          width={200}
          height={200}
        />

        <div className="flex flex-1/2 flex-col">
          <p>
            <strong>{name} info</strong>
          </p>
          <p>Employees: {employees}</p>
          <p>Fouls: {fouls}</p>

          <div className="flex flex-row *:p-1 *:m-1">
            <button className="bg-red-600 w-10 text-white rounded hover:bg-red-950 cursor-pointer">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                <path d="M5 18h1.5a1.5 1.5 0 0 0 0 -3h-1.5v6" />
                <path d="M17 18h2" />
                <path d="M20 15h-3v6" />
                <path d="M11 15v6h1a2 2 0 0 0 2 -2v-2a2 2 0 0 0 -2 -2h-1z" />
              </svg>
            </button>
            <button className="bg-blue-600 w-10 rounded text-white hover:bg-blue-950 cursor-pointer">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                <path d="M2 15v6h1a2 2 0 0 0 2 -2v-2a2 2 0 0 0 -2 -2h-1z" />
                <path d="M17 16.5a1.5 1.5 0 0 0 -3 0v3a1.5 1.5 0 0 0 3 0" />
                <path d="M9.5 15a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1 -3 0v-3a1.5 1.5 0 0 1 1.5 -1.5z" />
                <path d="M19.5 15l3 6" />
                <path d="M19.5 21l3 -6" />
              </svg>
            </button>
            <button className="bg-green-600 w-10 text-white rounded hover:bg-green-950 cursor-pointer">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path stroke="none" d="M0 0h24v24H0z" fill="none" />
                <path d="M14 3v4a1 1 0 0 0 1 1h4" />
                <path d="M5 12v-7a2 2 0 0 1 2 -2h7l5 5v4" />
                <path d="M4 15l4 6" />
                <path d="M4 21l4 -6" />
                <path d="M17 20.25c0 .414 .336 .75 .75 .75h1.25a1 1 0 0 0 1 -1v-1a1 1 0 0 0 -1 -1h-1a1 1 0 0 1 -1 -1v-1a1 1 0 0 1 1 -1h1.25a.75 .75 0 0 1 .75 .75" />
                <path d="M11 15v6h3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </>
  );
};
