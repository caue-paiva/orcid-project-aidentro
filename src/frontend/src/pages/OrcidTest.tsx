import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import OrcidAuth from '@/components/OrcidAuth';
import { checkOauthStatus } from '@/api/orcidApi';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const OrcidTest: React.FC = () => {
  const handleCheckBackendStatus = async () => {
    try {
      const status = await checkOauthStatus();
      console.log('Backend OAuth Status:', status);
      toast.success('Backend is connected! Check console for details.');
    } catch (error) {
      console.error('Backend connection failed:', error);
      toast.error('Failed to connect to backend. Check console for details.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            ORCID Authentication Test
          </h1>
          <p className="text-gray-600">
            Test the integration between React frontend and Django backend
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* ORCID Auth Component */}
          <Card>
            <CardHeader>
              <CardTitle>ORCID Authentication</CardTitle>
            </CardHeader>
            <CardContent>
              <OrcidAuth />
            </CardContent>
          </Card>

          {/* Backend Status Test */}
          <Card>
            <CardHeader>
              <CardTitle>Backend Connection Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
                Test the connection to your Django backend
              </p>
              <Button 
                onClick={handleCheckBackendStatus}
                className="w-full"
              >
                Check Backend Status
              </Button>
              <div className="text-xs text-gray-500 space-y-1">
                <p><strong>Backend URL:</strong> http://localhost:8000</p>
                <p><strong>Test Endpoint:</strong> /oauth/status/</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>How to Test</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <ol className="list-decimal list-inside space-y-2 text-gray-700">
                <li>Make sure your Django backend is running on <code>http://localhost:8000</code></li>
                <li>Click "Check Backend Status" to verify the connection</li>
                <li>Click "Sign in with ORCID" to start the OAuth flow</li>
                <li>You'll be redirected to ORCID for authentication</li>
                <li>After authentication, you'll be redirected back to the success page</li>
                <li>Check the Django logs to see the access token and ORCID ID</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        {/* API Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle>Available API Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Backend Endpoints:</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• <code>GET /oauth/status/</code> - OAuth config status</li>
                  <li>• <code>GET /oauth/authorize/</code> - Start OAuth flow</li>
                  <li>• <code>GET /oauth/callback/</code> - OAuth callback</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Frontend Routes:</h4>
                <ul className="space-y-1 text-gray-600">
                  <li>• <code>/auth/success</code> - Success callback</li>
                  <li>• <code>/auth/error</code> - Error callback</li>
                  <li>• <code>/signin</code> - Sign in page</li>
                  <li>• <code>/orcid-test</code> - This test page</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default OrcidTest; 