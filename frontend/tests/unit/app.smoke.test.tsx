import { render, screen } from '@testing-library/react';

import App from '@/App';

describe('App', () => {
  it('renders the onboarding placeholder', () => {
    render(<App />);

    expect(screen.getByText('[Screen: onboarding]')).toBeInTheDocument();
  });
});
