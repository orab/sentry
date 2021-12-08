import * as React from 'react';

import SvgIcon, {SVGIconProps} from './svgIcon';

const IconSound = React.forwardRef<SVGSVGElement, SVGIconProps>(function IconSound(
  props: SVGIconProps,
  ref: React.Ref<SVGSVGElement>
) {
  return (
    <SvgIcon {...props} ref={ref}>
      <path d="M6.825 10.7114H4.875C4.8 10.7114 4.65 10.7114 4.575 10.6364L2.25 9.06143H0.6C0.225 9.06143 0 8.76143 0 8.46143V3.88643C0 3.58643 0.225 3.28643 0.6 3.28643H2.25L4.5 1.78643C4.65 1.71143 4.725 1.71143 4.875 1.71143H6.825C7.125 1.71143 7.425 1.93643 7.425 2.31143V10.1864C7.35 10.4114 7.125 10.7114 6.825 10.7114ZM5.025 9.58643H6.225V2.83643H5.025L2.7 4.41143C2.625 4.41143 2.55 4.48643 2.4 4.48643H1.125V7.93643H2.4C2.475 7.93643 2.625 7.93643 2.7 8.01143L5.025 9.58643Z" />
      <path d="M10.4249 9.06133C10.3499 9.06133 10.2749 9.06133 10.1999 8.98633C9.89985 8.83633 9.82485 8.53633 9.97485 8.23633C9.97485 8.16133 10.0499 8.16133 10.0499 8.08633C11.0999 7.03633 11.0999 5.31133 10.0499 4.26133C9.82485 4.03633 9.82485 3.66133 10.0499 3.43633C10.2749 3.21133 10.6499 3.21133 10.8749 3.43633C12.3749 4.93633 12.3749 7.33633 10.8749 8.83633C10.7249 8.98633 10.5749 9.06133 10.4249 9.06133Z" />
      <path d="M8.7752 8.01133C8.6252 8.01133 8.4752 7.93633 8.4002 7.86133C8.1752 7.63633 8.1752 7.26133 8.4002 7.03633C8.6252 6.81133 8.7752 6.51133 8.7752 6.21133C8.7752 5.91133 8.6252 5.61133 8.4002 5.38633C8.1752 5.16133 8.1752 4.78633 8.4002 4.56133C8.6252 4.33633 9.0002 4.33633 9.2252 4.56133C9.6752 5.01133 9.9002 5.53633 9.9002 6.21133C9.9002 6.81133 9.6752 7.41133 9.2252 7.86133C9.0752 7.93633 8.9252 8.01133 8.7752 8.01133Z" />
    </SvgIcon>
  );
});

IconSound.displayName = 'IconSound';

export {IconSound};
