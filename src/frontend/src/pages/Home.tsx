
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SearchIcon, UsersIcon, BookIcon } from "lucide-react";

const Home = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-white to-gray-50 py-16 md:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-gray-900">
              Connect Your <span className="text-orcid-green">Research</span>
              <br /> and <span className="text-orcid-green">Identity</span>
            </h1>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              ORCID provides a persistent digital identifier that distinguishes you
              from every other researcher. Connect your ID with your professional
              information: affiliations, grants, publications, peer review, and more.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register">
                <Button className="bg-orcid-green hover:bg-orcid-green/90 text-white px-8 py-6 text-lg">
                  Register for free
                </Button>
              </Link>
              <Link to="/about">
                <Button variant="outline" className="px-8 py-6 text-lg">
                  Learn more
                </Button>
              </Link>
            </div>
          </div>

          <div className="mt-16 md:mt-24 flex justify-center">
            <div className="bg-white shadow-lg rounded-2xl p-6 md:p-10 max-w-4xl mx-auto">
              <div className="flex flex-col md:flex-row items-center">
                <div className="h-20 w-20 rounded-full bg-orcid-green flex items-center justify-center">
                  <span className="font-bold text-white text-3xl">ID</span>
                </div>
                <div className="mt-4 md:mt-0 md:ml-8 text-center md:text-left">
                  <h2 className="text-2xl font-semibold">What is an ORCID iD?</h2>
                  <p className="mt-2 text-gray-600">
                    Your ORCID iD is a unique, persistent identifier for you as a researcher
                    that helps ensure your work is recognized. Over 10 million researchers
                    worldwide already have an ORCID iD.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">Why use ORCID?</h2>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              ORCID connects researchers with their research to enhance scientific discovery and innovation.
            </p>
          </div>

          <div className="mt-16 grid gap-8 md:grid-cols-3">
            <Card className="shadow-md hover:shadow-xl transition-shadow border-t-4 border-t-orcid-green">
              <CardHeader>
                <div className="bg-accent w-12 h-12 rounded-full flex items-center justify-center mb-4">
                  <SearchIcon className="h-6 w-6 text-orcid-green" />
                </div>
                <CardTitle>Distinguish Yourself</CardTitle>
                <CardDescription>
                  Stand out in a crowd of researchers with similar names.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>
                  Your ORCID iD is a unique identifier that distinguishes you from every
                  other researcher, ensuring your work is recognized.
                </p>
              </CardContent>
              <CardFooter>
                <Link to="/researchers/benefits">
                  <Button variant="link" className="text-orcid-green p-0">
                    Learn more
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            <Card className="shadow-md hover:shadow-xl transition-shadow border-t-4 border-t-orcid-green">
              <CardHeader>
                <div className="bg-accent w-12 h-12 rounded-full flex items-center justify-center mb-4">
                  <UsersIcon className="h-6 w-6 text-orcid-green" />
                </div>
                <CardTitle>Connect Your Research</CardTitle>
                <CardDescription>
                  Link your iD to your publications, grants, and affiliations.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>
                  ORCID connects you with your research activities, ensuring proper
                  attribution and reducing administrative burden.
                </p>
              </CardContent>
              <CardFooter>
                <Link to="/researchers/tools">
                  <Button variant="link" className="text-orcid-green p-0">
                    Learn more
                  </Button>
                </Link>
              </CardFooter>
            </Card>

            <Card className="shadow-md hover:shadow-xl transition-shadow border-t-4 border-t-orcid-green">
              <CardHeader>
                <div className="bg-accent w-12 h-12 rounded-full flex items-center justify-center mb-4">
                  <BookIcon className="h-6 w-6 text-orcid-green" />
                </div>
                <CardTitle>Increase Visibility</CardTitle>
                <CardDescription>
                  Gain recognition for all your research outputs.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p>
                  Increase the visibility of your entire research portfolio, including
                  publications, datasets, peer reviews, and more.
                </p>
              </CardContent>
              <CardFooter>
                <Link to="/researchers">
                  <Button variant="link" className="text-orcid-green p-0">
                    Learn more
                  </Button>
                </Link>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">
              ORCID by the Numbers
            </h2>
          </div>

          <div className="mt-12 grid grid-cols-2 gap-8 md:grid-cols-4">
            <div className="bg-white p-6 rounded-2xl shadow-md">
              <p className="text-4xl font-bold text-orcid-green">10M+</p>
              <p className="mt-2 text-sm font-medium text-gray-600">Registered Users</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-md">
              <p className="text-4xl font-bold text-orcid-green">1,300+</p>
              <p className="mt-2 text-sm font-medium text-gray-600">Member Organizations</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-md">
              <p className="text-4xl font-bold text-orcid-green">130+</p>
              <p className="mt-2 text-sm font-medium text-gray-600">Countries & Territories</p>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-md">
              <p className="text-4xl font-bold text-orcid-green">50M+</p>
              <p className="mt-2 text-sm font-medium text-gray-600">Connected Works</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-orcid-green/90 to-orcid-green">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white">
            Ready to enhance your research identity?
          </h2>
          <p className="mt-4 text-xl text-white/90 max-w-3xl mx-auto">
            Join millions of researchers worldwide who use ORCID to distinguish themselves and their contributions.
          </p>
          <div className="mt-10">
            <Link to="/register">
              <Button className="bg-white text-orcid-green hover:bg-gray-100 px-8 py-6 text-lg font-semibold">
                Register now
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
