import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

const AuthSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const orcidId = searchParams.get('orcid_id');
    
    if (orcidId) {
      // Store ORCID ID in localStorage
      localStorage.setItem('orcid_id', orcidId);
      localStorage.setItem('orcid_authenticated', 'true');
      
      console.log('ORCID authentication successful!', orcidId);
      
      // Redirect to dashboard after a brief delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1000);
    } else {
      console.error('No ORCID ID found in callback');
      navigate('/dashboard');
    }
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto h-12 w-12 text-green-600">
            <svg
              className="animate-spin h-12 w-12"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            ORCID Authentication Successful!
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Redirecting to your dashboard...
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthSuccess; 