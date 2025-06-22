
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckCircle2, CircleDot } from "lucide-react";
import { Link } from "react-router-dom";
import { Researcher } from "@/types";

interface ProfileCompletionProps {
  researcher: Researcher;
}

const ProfileCompletion = ({ researcher }: ProfileCompletionProps) => {
  // Tasks to complete profile
  const tasks = [
    {
      name: "Add personal information",
      completed: !!researcher.name && !!researcher.country,
      link: "/profile/edit"
    },
    {
      name: "Add professional information",
      completed: !!researcher.institutionName && !!researcher.position,
      link: "/profile/edit"
    },
    {
      name: "Add biography",
      completed: !!researcher.biography,
      link: "/profile/edit"
    },
    {
      name: "Select research areas",
      completed: researcher.areaOfExpertise.length > 0,
      link: "/profile/edit"
    },
    {
      name: "Add publications",
      completed: researcher.metrics.publications > 0,
      link: "/publications/import"
    }
  ];

  const completedTasks = tasks.filter(task => task.completed).length;
  const completionPercentage = (completedTasks / tasks.length) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Completion</CardTitle>
        <CardDescription>
          Complete your profile to increase visibility
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-5">
          <div>
            <div className="flex justify-between mb-1 text-sm">
              <span>Progress</span>
              <span className="font-medium">{completionPercentage.toFixed()}%</span>
            </div>
            <Progress value={completionPercentage} className="h-2" />
          </div>

          <div className="space-y-3">
            {tasks.map((task, index) => (
              <div key={index} className="flex items-center space-x-3">
                {task.completed ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <CircleDot className="h-5 w-5 text-gray-400" />
                )}
                <span className={`text-sm ${task.completed ? "line-through text-gray-500" : ""}`}>
                  {task.name}
                </span>
                {!task.completed && (
                  <Link to={task.link} className="text-xs text-orcid-green hover:underline ml-auto">
                    Complete
                  </Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
      {completionPercentage < 100 && (
        <CardFooter>
          <Link to="/profile/edit" className="w-full">
            <Button className="w-full bg-orcid-green hover:bg-orcid-green/90">
              Complete your profile
            </Button>
          </Link>
        </CardFooter>
      )}
    </Card>
  );
};

export default ProfileCompletion;
