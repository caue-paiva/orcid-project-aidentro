
import { Link } from "react-router-dom";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    {
      title: "About",
      links: [
        { name: "What is ORCID", href: "/about" },
        { name: "Our Mission", href: "/about/mission" },
        { name: "Our Team", href: "/about/team" },
        { name: "Contact Us", href: "/about/contact" },
      ],
    },
    {
      title: "Resources",
      links: [
        { name: "For Researchers", href: "/researchers" },
        { name: "For Organizations", href: "/membership" },
        { name: "Documentation", href: "/documentation" },
        { name: "API", href: "/documentation/api" },
      ],
    },
    {
      title: "Community",
      links: [
        { name: "News & Events", href: "/news" },
        { name: "Blog", href: "/news/blog" },
        { name: "Success Stories", href: "/researchers/stories" },
        { name: "Get Involved", href: "/get-involved" },
      ],
    },
  ];

  return (
    <footer className="bg-gray-50 mt-auto">
      <div className="max-w-7xl mx-auto pt-12 px-4 sm:px-6 lg:px-8">
        <div className="xl:grid xl:grid-cols-4 xl:gap-8">
          <div className="space-y-4 xl:col-span-1">
            <div className="flex items-center space-x-2">
              <div className="h-10 w-10 rounded-full bg-orcid-green flex items-center justify-center">
                <span className="font-bold text-white text-lg">ID</span>
              </div>
              <span className="font-bold text-2xl">ORCID</span>
            </div>
            <p className="text-gray-600 text-sm">
              ORCID provides a persistent digital identifier that you own and control, distinguishing you from every other researcher.
            </p>
            <div className="flex space-x-4 mt-4">
              <a href="https://twitter.com/orcid_org" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-orcid-green">
                <span className="sr-only">Twitter</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                </svg>
              </a>
              <a href="https://www.linkedin.com/company/orcid" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-orcid-green">
                <span className="sr-only">LinkedIn</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                </svg>
              </a>
              <a href="https://youtube.com/orcid" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-orcid-green">
                <span className="sr-only">YouTube</span>
                <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
              </a>
            </div>
          </div>
          <div className="mt-12 grid grid-cols-3 gap-8 xl:mt-0 xl:col-span-3">
            {footerLinks.map((group) => (
              <div key={group.title} className="md:grid md:grid-cols-1">
                <h3 className="text-sm font-semibold text-gray-800 tracking-wider uppercase">
                  {group.title}
                </h3>
                <ul className="mt-4 space-y-2">
                  {group.links.map((link) => (
                    <li key={link.name}>
                      <Link
                        to={link.href}
                        className="text-sm text-gray-600 hover:text-orcid-green"
                      >
                        {link.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-gray-200 pb-8">
          <p className="text-sm text-gray-500">
            © {currentYear} ORCID. All rights reserved.
          </p>
          <div className="mt-2 flex space-x-6">
            <Link to="/privacy" className="text-sm text-gray-500 hover:text-orcid-green">
              Privacy Policy
            </Link>
            <Link to="/terms" className="text-sm text-gray-500 hover:text-orcid-green">
              Terms of Service
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
