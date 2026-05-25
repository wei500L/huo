import { render, screen } from '@testing-library/react';

import App from '@/App';

describe('App', () => {
  it('renders the onboarding screen', () => {
    render(<App />);

    expect(screen.getByText('欢迎，新任 CEO')).toBeInTheDocument();
  });
});
