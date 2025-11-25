import type { JSX } from "react";
import { signIn } from "../auth/signIn";

interface ProtectedRouteProps {
  children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const isAuthenticated = false;
  if (!isAuthenticated) {
    return signIn();
  }
  return children;
};

export default ProtectedRoute;
