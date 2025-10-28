// import { useState } from "react";

const getTotalEmployees = async () => {
  try {
    const response = await fetch("127.0.0.1:8000/api/employees");
    // const [employee, setEmployee] = useState(0);

    if (!response) return "No response";

    const data = await response.json();

    return data;
  } catch (error) {
    console.error(`Error: ${error}`);
  }
};

getTotalEmployees();
