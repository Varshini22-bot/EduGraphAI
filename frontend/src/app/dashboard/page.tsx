"use client";

import { useAuth } from "@/hooks/useAuth";

export default function Dashboard() {

  const { user } = useAuth();

  return (

    <div className="p-10">

      <h1 className="text-4xl font-bold">

        Welcome

      </h1>

      <p className="mt-4">

        {user?.email}

      </p>

    </div>

  );

}