import * as Sentry from '@sentry/react';
import {render, screen, waitFor} from '@testing-library/react';
import * as devicelist from 'ios-device-list';

import * as Device from 'sentry/components/deviceName';

jest.mock('ios-device-list');

describe('DeviceName', () => {
  it('renders nothing if value is null', async () => {
    render(<Device.DeviceName value={undefined} />);

    await waitFor(() =>
      expect(screen.queryByTestId(/loaded-device-name/)).not.toBeInTheDocument()
    );
  });

  it('renders device name if module is loaded', async () => {
    devicelist.generationByIdentifier.mockImplementation(() => 'iPhone 6s Plus');

    render(<Device.DeviceName value="iPhone8,2" />);

    expect(await screen.findByText('iPhone 6s Plus')).toBeInTheDocument();
    expect(devicelist.generationByIdentifier).toHaveBeenCalledWith('iPhone8,2');
  });

  it('renders device name if name helper returns undefined is loaded', async () => {
    devicelist.generationByIdentifier.mockImplementation(() => undefined);

    render(<Device.DeviceName value="iPhone8,2" />);

    expect(await screen.findByText('iPhone8,2')).toBeInTheDocument();
    expect(devicelist.generationByIdentifier).toHaveBeenCalledWith('iPhone8,2');
  });

  it('renders device name if module is not loaded', async () => {
    jest.spyOn(Device, 'loadiOSDeviceListModule').mockImplementation(() => {
      return Promise.reject('Cannot load module');
    });

    const spy = jest.spyOn(Sentry, 'captureException');

    render(<Device.DeviceName value="iPhone8,2" />);

    await waitFor(() =>
      expect(spy).toHaveBeenCalledWith('Failed to load ios-device-list module')
    );

    expect(await screen.findByText('iPhone8,2')).toBeInTheDocument();
  });
});
