import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { XCircle, RotateCcw } from 'lucide-react';

const AuthError: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  const [errorDescription, setErrorDescription] = useState<string>('');

  useEffect(() => {
    const errorCode = searchParams.get('error');
    const description = searchParams.get('description');
    
    setError(errorCode || 'unknown_error');
    setErrorDescription(description || 'An unknown error occurred during authentication.');
  }, [searchParams]);

  const handleTryAgain = () => {
    navigate('/signin');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  const getErrorMessage = (errorCode: string) => {
    switch (errorCode) {
      case 'access_denied':
        return 'You denied access to your ORCID account.';
      case 'no_code':
        return 'No authorization code was received from ORCID.';
      case 'token_exchange_failed':
        return 'Failed to exchange authorization code for access token.';
      default:
        return 'An unexpected error occurred during authentication.';
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <XCircle className="w-8 h-8 text-red-600" />
          </div>
          <CardTitle className="text-2xl text-red-800">
            Authentication Failed
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-4">
          <p className="text-gray-600">
            {getErrorMessage(error)}
          </p>
          
          {errorDescription && errorDescription !== getErrorMessage(error) && (
            <div className="bg-red-50 p-3 rounded-lg text-left">
              <p className="text-sm text-red-500 mb-1">Error Details:</p>
              <p className="text-sm text-red-700">{errorDescription}</p>
            </div>
          )}

          <div className="bg-gray-50 p-3 rounded-lg text-left">
            <p className="text-sm text-gray-500 mb-1">Error Code:</p>
            <p className="font-mono text-sm font-semibold">{error}</p>
          </div>

          <div className="space-y-2 pt-4">
            <Button 
              onClick={handleTryAgain} 
              className="w-full"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Try Again
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

export default AuthError; 