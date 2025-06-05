import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle } from 'lucide-react';

const AuthSuccess: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [orcidId, setOrcidId] = useState<string | null>(null);

  useEffect(() => {
    const orcid = searchParams.get('orcid_id');
    if (orcid) {
      setOrcidId(orcid);
      // Store in localStorage or global state if needed
      localStorage.setItem('orcid_id', orcid);
    }
  }, [searchParams]);

  const handleContinue = () => {
    navigate('/dashboard');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <CardTitle className="text-2xl text-green-800">
            ORCID Authentication Successful!
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p className="text-gray-600">
            Your ORCID account has been successfully connected.
          </p>
          
          {orcidId && (
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-500 mb-1">Your ORCID ID:</p>
              <p className="font-mono text-sm font-semibold">{orcidId}</p>
            </div>
          )}

          <div className="space-y-2 pt-4">
            <Button 
              onClick={handleContinue} 
              className="w-full"
            >
              Continue to Dashboard
            </Button>
            <Button 
              onClick={handleGoHome} 
              variant="outline" 
              className="w-full"
            >
              Go to Home
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthSuccess; 