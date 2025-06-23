import { ExternalLink, User, Plus } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { SocialMediaAccount } from "@/api/orcidApi";

interface SocialMediaCardProps {
  socialMediaAccounts: SocialMediaAccount[];
  isLoading?: boolean;
  error?: string;
  isAuthenticated?: boolean;
  onAddAccount?: () => void;
}

// Social media platform icons and colors
const platformConfig: Record<string, { icon: string; color: string; displayName: string }> = {
  twitter: { icon: "🐦", color: "text-blue-500", displayName: "Twitter" },
  x: { icon: "✖️", color: "text-black", displayName: "X (Twitter)" },
  instagram: { icon: "📷", color: "text-pink-500", displayName: "Instagram" },
  youtube: { icon: "📺", color: "text-red-500", displayName: "YouTube" },
  linkedin: { icon: "💼", color: "text-blue-600", displayName: "LinkedIn" },
  facebook: { icon: "📘", color: "text-blue-700", displayName: "Facebook" },
  github: { icon: "💻", color: "text-gray-800", displayName: "GitHub" },
  researchgate: { icon: "🔬", color: "text-green-600", displayName: "ResearchGate" },
  google_scholar: { icon: "🎓", color: "text-blue-800", displayName: "Google Scholar" },
  orcid: { icon: "🆔", color: "text-green-500", displayName: "ORCID" },
  mastodon: { icon: "🐘", color: "text-purple-600", displayName: "Mastodon" },
  tiktok: { icon: "🎵", color: "text-black", displayName: "TikTok" },
  snapchat: { icon: "👻", color: "text-yellow-500", displayName: "Snapchat" },
};

const SocialMediaCard = ({ 
  socialMediaAccounts, 
  isLoading = false, 
  error, 
  isAuthenticated = false,
  onAddAccount 
}: SocialMediaCardProps) => {
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-4 w-4 mr-2 text-blue-500" />
            Social Media
          </CardTitle>
          <CardDescription>Loading social media accounts...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="h-4 w-4 mr-2 text-blue-500" />
            Social Media
          </CardTitle>
          <CardDescription>Error loading social media accounts</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <User className="h-4 w-4 mr-2 text-blue-500" />
            Social Media
          </div>
          {onAddAccount && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onAddAccount}
              className="h-8 w-8 p-0 hover:bg-blue-50"
              title="Add social media account"
            >
              <Plus className="h-5 w-5 text-blue-600" />
            </Button>
          )}
        </CardTitle>
        <CardDescription>
          {socialMediaAccounts.length > 0 
            ? `${socialMediaAccounts.length} social media account${socialMediaAccounts.length !== 1 ? 's' : ''}`
            : "No social media accounts found"
          }
        </CardDescription>
      </CardHeader>
      <CardContent>
        {socialMediaAccounts.length > 0 ? (
          <div className="space-y-3">
            {socialMediaAccounts.map((account, index) => {
              const config = platformConfig[account.platform.toLowerCase()] || {
                icon: "🔗",
                color: "text-gray-600",
                displayName: account.platform
              };
              
              return (
                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{config.icon}</span>
                    <div>
                      <div className="font-medium text-sm">{config.displayName}</div>
                      <div className="text-xs text-gray-600">@{account.username}</div>
                    </div>
                  </div>
                  <a
                    href={account.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-4">
            <div className="text-gray-400 mb-2">
              <User className="h-8 w-8 mx-auto" />
            </div>
            <p className="text-sm text-gray-600">
              {isAuthenticated 
                ? "No social media accounts added yet" 
                : "No public social media accounts"
              }
            </p>
            {onAddAccount && (
              <Button
                variant="outline"
                size="sm"
                onClick={onAddAccount}
                className="mt-2"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Account
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default SocialMediaCard; 