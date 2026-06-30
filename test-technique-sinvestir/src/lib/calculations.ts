export const calculateCompoundInterest = (
  initial: number,
  monthly: number,
  years: number,
  rate: number
) => {
  const monthlyRate = rate / 100 / 12;
  const months = years * 12;
  
  const finalCapital = 
    initial * Math.pow(1 + monthlyRate, months) +
    monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);

  const totalInvested = initial + (monthly * months);
  
  return {
    finalCapital: Math.round(finalCapital),
    totalInvested: Math.round(totalInvested),
    totalInterests: Math.round(finalCapital - totalInvested),
  };
};
