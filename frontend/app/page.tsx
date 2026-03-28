import {
  Button,
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  Separator,
} from "@heroui/react";
import Image from "next/image";

export default function Home() {
  return (
    <div className="w-full h-screen flex justify-center items-center">
      <Card variant="tertiary">
        <CardHeader>
          <CardTitle className="font-semibold">Rate Tracker Frontend</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <p className="text-sm text-warning">
            Track your rates and stay updated with the latest market trends.
          </p>
          <ul className="flex flex-col gap-2 list-disc pl-5 text-sm">
            <li>
              <strong>Rate Comparison Table:</strong> A table displaying the
              latest rate per provider that is sortable by both rate value and
              last-updated date.
            </li>
            <li>
              <strong>Historical Line Chart:</strong> A visual representation of
              30-day history for a provider and rate type selected by the user.
            </li>
            <li>
              <strong>Automatic Background Refresh:</strong> The data must
              auto-refresh every 60 seconds without requiring a full page
              reload.
            </li>
            <li>
              <strong>State Visibility:</strong> Every data fetch must have a
              visible loading state and error state (the instructions specify
              that a simple spinner is not sufficient).
            </li>
            <li>
              <strong>Responsive Design:</strong> The layout must be fully
              functional on mobile devices with a 375px-wide viewport.
            </li>
            <li>
              <strong>Local Access:</strong> Once the stack is running via{" "}
              <code>docker-compose up</code>, the dashboard must be accessible
              at <code>localhost:3000</code>.
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
