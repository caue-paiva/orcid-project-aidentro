
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue
} from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Check, ChevronRight, UserCheck } from "lucide-react";
import { countries, expertiseAreas, institutions, newUser } from "@/data/mockData";
import { toast } from "sonner";

const steps = [
  { id: 1, name: "Personal Info" },
  { id: 2, name: "Import Publications" },
  { id: 3, name: "Research Areas" },
  { id: 4, name: "Complete" }
];

const Onboarding = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [user, setUser] = useState(newUser);
  const [selectedAreas, setSelectedAreas] = useState<string[]>([]);
  const navigate = useNavigate();

  const updateUser = (field: string, value: any) => {
    setUser((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
      // Update onboarding step in user object
      updateUser("onboardingStep", currentStep);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleFinish = () => {
    toast.success("Onboarding completed! Welcome to ORCID.");
    navigate("/dashboard");
  };

  const handleCheckboxChange = (area: string) => {
    setSelectedAreas((prev) => {
      if (prev.includes(area)) {
        return prev.filter((item) => item !== area);
      } else {
        return [...prev, area];
      }
    });
  };

  const progressPercentage = ((currentStep - 1) / (steps.length - 1)) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-12">
          <div className="mx-auto h-16 w-16 rounded-full bg-orcid-green flex items-center justify-center">
            <UserCheck className="h-8 w-8 text-white" />
          </div>
          <h1 className="mt-6 text-3xl font-bold text-gray-900">
            Complete Your Profile
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Let's set up your researcher profile to make the most of ORCID.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <Progress value={progressPercentage} className="h-2" />
          <div className="mt-2 flex justify-between">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`flex flex-col items-center ${
                  step.id <= currentStep
                    ? "text-orcid-green"
                    : "text-gray-400"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                    step.id < currentStep
                      ? "bg-orcid-green text-white"
                      : step.id === currentStep
                      ? "border-2 border-orcid-green text-orcid-green"
                      : "border-2 border-gray-300 text-gray-400"
                  }`}
                >
                  {step.id < currentStep ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    step.id
                  )}
                </div>
                <span className="mt-1 text-xs hidden sm:block">{step.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <Card className="shadow-lg">
          <div className="p-6 sm:p-8">
            {currentStep === 1 && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Personal Information</h2>
                <p className="text-gray-600">
                  Tell us about yourself and your affiliation.
                </p>

                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name</Label>
                    <Input 
                      id="firstName" 
                      value={user.name.split(' ')[0]}
                      onChange={(e) => updateUser('name', `${e.target.value} ${user.name.split(' ')[1] || ''}`)}
                      required 
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input 
                      id="lastName" 
                      value={user.name.split(' ').slice(1).join(' ')}
                      onChange={(e) => updateUser('name', `${user.name.split(' ')[0]} ${e.target.value}`)}
                      required 
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="your.email@institution.edu" 
                    onChange={(e) => updateUser('email', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="institution">Primary Institution</Label>
                  <Select onValueChange={(value) => updateUser('institutionName', institutions.find(i => i.value === value)?.label || '')}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select your institution" />
                    </SelectTrigger>
                    <SelectContent>
                      {institutions.map((institution) => (
                        <SelectItem key={institution.value} value={institution.value}>
                          {institution.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="country">Country</Label>
                  <Select 
                    onValueChange={(value) => {
                      const country = countries.find(c => c.value === value);
                      if (country) {
                        updateUser('countryCode', country.value);
                        updateUser('country', country.label);
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your country" />
                    </SelectTrigger>
                    <SelectContent>
                      {countries.map((country) => (
                        <SelectItem key={country.value} value={country.value}>
                          {country.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bio">Biography</Label>
                  <Textarea 
                    id="bio" 
                    placeholder="Tell us about your research background (optional)"
                    onChange={(e) => updateUser('biography', e.target.value)}
                    rows={4}
                  />
                </div>
              </div>
            )}

            {currentStep === 2 && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Import Publications</h2>
                <p className="text-gray-600">
                  Quickly add your existing publications to your ORCID profile.
                </p>

                <div className="space-y-4">
                  <div className="bg-white border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="text-blue-700"
                          >
                            <path d="M12 8V4H8" />
                            <rect width="16" height="12" x="4" y="8" rx="2" />
                            <path d="M2 14h2" />
                            <path d="M20 14h2" />
                            <path d="M15 13v2" />
                            <path d="M9 13v2" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">Google Scholar</h3>
                          <p className="text-sm text-gray-500">
                            Import publications from your Google Scholar profile
                          </p>
                        </div>
                      </div>
                      <Button 
                        onClick={() => toast.info("Google Scholar import wizard would open here")}
                        variant="outline"
                      >
                        Connect
                      </Button>
                    </div>
                  </div>

                  <div className="bg-white border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="text-blue-700"
                          >
                            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">Lattes</h3>
                          <p className="text-sm text-gray-500">
                            Import publications from your Lattes CV
                          </p>
                        </div>
                      </div>
                      <Button 
                        onClick={() => toast.info("Lattes import wizard would open here")}
                        variant="outline"
                      >
                        Connect
                      </Button>
                    </div>
                  </div>

                  <div className="bg-white border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="bg-blue-100 p-2 rounded-lg">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="24"
                            height="24"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="text-blue-700"
                          >
                            <path d="M21 9V3H15" />
                            <path d="M21 3l-7 7" />
                            <path d="M3 15c0 3.3 2.7 6 6 6s6-2.7 6-6-2.7-6-6-6h0" />
                            <path d="M3 15V9h6" />
                            <path d="M3 9l6 6" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="font-medium">Import by DOI</h3>
                          <p className="text-sm text-gray-500">
                            Add publications by their DOI
                          </p>
                        </div>
                      </div>
                      <Button 
                        onClick={() => toast.info("DOI import form would open here")}
                        variant="outline"
                      >
                        Import
                      </Button>
                    </div>
                  </div>

                  <p className="text-center text-sm text-gray-500 mt-4">
                    You can also import publications later from your dashboard.
                  </p>
                </div>
              </div>
            )}

            {currentStep === 3 && (
              <div className="space-y-6">
                <h2 className="text-xl font-semibold">Research Areas</h2>
                <p className="text-gray-600">
                  Select your areas of expertise to help others find your work.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {expertiseAreas.map((area) => (
                    <div key={area} className="flex items-center space-x-2">
                      <Checkbox 
                        id={area} 
                        checked={selectedAreas.includes(area)}
                        onCheckedChange={() => handleCheckboxChange(area)}
                      />
                      <label
                        htmlFor={area}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        {area}
                      </label>
                    </div>
                  ))}
                </div>

                <div className="pt-4">
                  <p className="text-sm text-gray-500">
                    Selected areas: <span className="font-medium">{selectedAreas.length}</span>
                  </p>
                </div>
              </div>
            )}

            {currentStep === 4 && (
              <div className="space-y-6 text-center">
                <div className="flex justify-center">
                  <div className="h-24 w-24 rounded-full bg-green-100 flex items-center justify-center">
                    <Check className="h-12 w-12 text-orcid-green" />
                  </div>
                </div>

                <h2 className="text-2xl font-semibold">Profile Setup Complete!</h2>
                <p className="text-gray-600">
                  Congratulations! Your ORCID profile is now set up. You can continue to customize your profile and add more information from your dashboard.
                </p>

                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="font-medium">Your ORCID iD:</p>
                  <p className="text-lg font-mono mt-2">{user.orcidId}</p>
                </div>

                <div className="pt-4">
                  <p className="text-sm text-gray-600">
                    Use this ID to be recognized for your research contributions across systems and publications.
                  </p>
                </div>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="mt-8 flex justify-between">
              <Button
                variant="ghost"
                onClick={handleBack}
                disabled={currentStep === 1}
              >
                Back
              </Button>
              {currentStep < steps.length ? (
                <Button onClick={handleNext} className="bg-orcid-green hover:bg-orcid-green/90">
                  Continue <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button onClick={handleFinish} className="bg-orcid-green hover:bg-orcid-green/90">
                  Go to Dashboard
                </Button>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Onboarding;
