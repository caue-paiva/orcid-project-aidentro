import { useState } from "react";
import { Plus, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface AddSocialMediaModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (platform: string, username: string) => Promise<void>;
  isLoading?: boolean;
}

// Available social media platforms
const socialMediaPlatforms = [
  { value: "twitter", label: "Twitter", icon: "🐦", placeholder: "username" },
  { value: "x", label: "X (Twitter)", icon: "✖️", placeholder: "username" },
  { value: "instagram", label: "Instagram", icon: "📷", placeholder: "username" },
  { value: "youtube", label: "YouTube", icon: "📺", placeholder: "channel_name" },
  { value: "linkedin", label: "LinkedIn", icon: "💼", placeholder: "username" },
  { value: "facebook", label: "Facebook", icon: "📘", placeholder: "username" },
  { value: "github", label: "GitHub", icon: "💻", placeholder: "username" },
  { value: "researchgate", label: "ResearchGate", icon: "🔬", placeholder: "profile_name" },
  { value: "google_scholar", label: "Google Scholar", icon: "🎓", placeholder: "user_id" },
  { value: "orcid", label: "ORCID", icon: "🆔", placeholder: "0000-0000-0000-0000" },
  { value: "mastodon", label: "Mastodon", icon: "🐘", placeholder: "username@instance.com" },
  { value: "tiktok", label: "TikTok", icon: "🎵", placeholder: "username" },
  { value: "snapchat", label: "Snapchat", icon: "👻", placeholder: "username" },
];

const AddSocialMediaModal = ({ isOpen, onClose, onSubmit, isLoading = false }: AddSocialMediaModalProps) => {
  const [selectedPlatform, setSelectedPlatform] = useState<string>("");
  const [username, setUsername] = useState<string>("");
  const [error, setError] = useState<string>("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!selectedPlatform) {
      setError("Please select a social media platform");
      return;
    }

    if (!username.trim()) {
      setError("Please enter a username");
      return;
    }

    try {
      await onSubmit(selectedPlatform, username.trim());
      // Reset form on success
      setSelectedPlatform("");
      setUsername("");
      onClose();
    } catch (error) {
      setError(error instanceof Error ? error.message : "Failed to add social media account");
    }
  };

  const handleClose = () => {
    setSelectedPlatform("");
    setUsername("");
    setError("");
    onClose();
  };

  const selectedPlatformData = socialMediaPlatforms.find(p => p.value === selectedPlatform);

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <Plus className="h-5 w-5 mr-2 text-blue-500" />
            Add Social Media Account
          </DialogTitle>
          <DialogDescription>
            Add a new social media account to your profile. Choose a platform and enter your username.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="platform">Social Media Platform</Label>
            <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
              <SelectTrigger>
                <SelectValue placeholder="Select a platform" />
              </SelectTrigger>
              <SelectContent>
                {socialMediaPlatforms.map((platform) => (
                  <SelectItem key={platform.value} value={platform.value}>
                    <div className="flex items-center">
                      <span className="mr-2">{platform.icon}</span>
                      {platform.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="username">
              Username
              {selectedPlatformData && (
                <span className="text-sm text-gray-500 ml-1">
                  (e.g., {selectedPlatformData.placeholder})
                </span>
              )}
            </Label>
            <Input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={selectedPlatformData?.placeholder || "Enter username"}
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !selectedPlatform || !username.trim()}
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Account
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AddSocialMediaModal; 