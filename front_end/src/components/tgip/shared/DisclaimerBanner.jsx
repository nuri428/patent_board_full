const DisclaimerBanner = ({ className = '' }) => (
  <p className={`text-xs text-slate-400 italic ${className}`}>
    This system provides observational signals with evidence. Final decisions remain with the user.
  </p>
);

export default DisclaimerBanner;
