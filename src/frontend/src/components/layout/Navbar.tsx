import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import UserInfoModal from "@/components/UserInfoModal";
import { getCurrentUserIdentity, UserIdentity } from "@/api/orcidApi";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Bell,
  Book,
  ChevronDown,
  LogIn,
  Menu,
  Search,
  User,
  X,
} from "lucide-react";
import { currentUser } from "@/data/mockData";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserModalOpen, setIsUserModalOpen] = useState(false);
  const [userIdentity, setUserIdentity] = useState<UserIdentity | null>(null);
  const isLoggedIn = !!currentUser?.isCompleteProfile;

  const mainNavItems = [
    { name: "Membership", href: "/membership" },
    { name: "Documentation", href: "/documentation" },
    { name: "News & Events", href: "/news" },
    { name: "Resources", href: "/resources", hasDropdown: true },
    { name: "For Researchers", href: "/researchers", hasDropdown: true },
  ];

  const researcherDropdownItems = [
    { name: "Benefits", href: "/researchers/benefits" },
    { name: "Tools", href: "/researchers/tools" },
    { name: "Success Stories", href: "/researchers/stories" },
  ];

  const resourcesDropdownItems = [
    { name: "FAQs", href: "/resources/faqs" },
    { name: "Tutorials", href: "/resources/tutorials" },
    { name: "Templates", href: "/resources/templates" },
  ];

  // Load user identity on component mount
  useEffect(() => {
    const loadUserIdentity = async () => {
      if (isLoggedIn) {
        try {
          const identity = await getCurrentUserIdentity();
          setUserIdentity(identity);
        } catch (error) {
          // Silently handle error - user can still click to try again
        }
      }
    };

    loadUserIdentity();
  }, [isLoggedIn]);

  return (
    <nav className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-orcid-green flex items-center justify-center">
              <span className="font-bold text-white">ID</span>
            </div>
            <span className="font-bold text-xl hidden md:block">ORCID</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center">
            {/* Links sem dropdown */}
            <div className="flex items-center space-x-6">
              {mainNavItems
                .filter((item) => !item.hasDropdown)
                .map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-700 hover:text-orcid-green font-medium"
                  >
                    {item.name}
                  </Link>
                ))}
            </div>

            {/* Divisória */}
            <div className="border-l border-gray-300 h-6 mx-4"></div>

            {/* Itens com dropdown */}
            <div className="flex items-center space-x-3">
              {mainNavItems
                .filter((item) => item.hasDropdown)
                .map((item) => (
                  <DropdownMenu key={item.name}>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        className="flex items-center space-x-1 text-gray-700 hover:text-orcid-green"
                      >
                        <span>{item.name}</span>
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="center" className="bg-white">
                      {item.name === "For Researchers"
                        ? researcherDropdownItems.map((subItem) => (
                            <DropdownMenuItem key={subItem.name} asChild>
                              <Link
                                to={subItem.href}
                                className="w-full cursor-pointer"
                              >
                                {subItem.name}
                              </Link>
                            </DropdownMenuItem>
                          ))
                        : resourcesDropdownItems.map((subItem) => (
                            <DropdownMenuItem key={subItem.name} asChild>
                              <Link
                                to={subItem.href}
                                className="w-full cursor-pointer"
                              >
                                {subItem.name}
                              </Link>
                            </DropdownMenuItem>
                          ))}
                    </DropdownMenuContent>
                  </DropdownMenu>
                ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-3">
            <Link to="/search" className="text-gray-600 hover:text-orcid-green">
              <Search className="h-5 w-5" />
            </Link>

            {isLoggedIn ? (
              <>
                <Link
                  to="/notifications"
                  className="text-gray-600 hover:text-orcid-green"
                >
                  <Bell className="h-5 w-5" />
                </Link>
                <div className="hidden sm:flex items-center space-x-2">
                  {/* User Profile Modal Button */}
                  <Button 
                    variant="ghost" 
                    size="icon"
                    className="p-2"
                    onClick={async () => {
                      // Always try to fetch fresh identity if logged in, or set default if not
                      try {
                        const identity = await getCurrentUserIdentity();
                        setUserIdentity(identity || {
                          orcid_id: 'Unknown',
                          name: 'Unknown User',
                          email: undefined,
                          current_affiliation: undefined,
                          current_location: undefined,
                          profile_url: 'https://orcid.org',
                          authenticated: false
                        });
                      } catch (error) {
                        // Set default values for non-logged-in users
                        setUserIdentity({
                          orcid_id: 'Unknown',
                          name: 'Unknown User',
                          email: undefined,
                          current_affiliation: undefined,
                          current_location: undefined,
                          profile_url: 'https://orcid.org',
                          authenticated: false
                        });
                      }
                      setIsUserModalOpen(true);
                    }}
                  >
                    <User className="h-5 w-5" />
                  </Button>
                  
                  {/* Dashboard Link Button */}
                  <Link to="/dashboard">
                    <Button variant="ghost" className="py-1 px-3">
                      <span className="hidden md:block">Dashboard</span>
                      <span className="md:hidden">Dash</span>
                    </Button>
                  </Link>
                </div>
              </>
            ) : (
              <>
                <Link to="/register" className="hidden md:block">
                  <Button
                    variant="outline"
                    className="border-orcid-green text-orcid-green hover:bg-orcid-green hover:text-white"
                  >
                    Register
                  </Button>
                </Link>
                <Link to="/signin">
                  <Button className="bg-orcid-green hover:bg-orcid-green/90">
                    <LogIn className="h-4 w-4 mr-2" />
                    <span>Sign in</span>
                  </Button>
                </Link>
              </>
            )}

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="mt-3 py-2 border-t lg:hidden">
            <div className="space-y-2 pt-2 pb-3">
              {mainNavItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="block px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-orcid-green rounded-md"
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.name}
                </Link>
              ))}
              {!isLoggedIn && (
                <Link
                  to="/register"
                  className="block px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-orcid-green rounded-md md:hidden"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Register
                </Link>
              )}
              {isLoggedIn && (
                <Link
                  to="/dashboard"
                  className="block px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-orcid-green rounded-md sm:hidden"
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </Link>
              )}
            </div>
          </div>
        )}
      </div>

            {/* User Info Modal */}
      {isUserModalOpen && userIdentity && (
        <UserInfoModal
          isOpen={isUserModalOpen}
          onClose={() => setIsUserModalOpen(false)}
          userIdentity={userIdentity}
        />
      )}


      </nav>
  );
};

export default Navbar;
