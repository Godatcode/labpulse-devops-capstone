# Interface references

Each note records a detail to consider, not a layout to copy.

## Equipment and maintenance software

- [Snipe-IT](https://snipe-it.readme.io/docs/introduction): an asset has an individual identity, location, and state. LabPulse should make the equipment ID visible beside every incident.
- [Agilent CrossLab Connect](https://www.agilent.com/en/s/software-lab-management/crosslab-connect): fleet status and service history belong in the same workflow. A coordinator should reach a fault from the equipment overview.
- [Labguru equipment management](https://www.labguru.com/equipment): calibration and maintenance dates are separate from incident reports. LabPulse should label the latter clearly rather than call every item a task.

## Product craft outside this category

- [Linear features](https://linear.app/features): planning, work, and insight have distinct navigation labels. LabPulse can keep equipment and incidents separate without hiding either behind a generic dashboard.
- [Vercel dashboard redesign](https://vercel.com/blog/dashboard-redesign): the production state and latest deployment are visible before logs. LabPulse should put current lab state before history.
- [Stripe Dashboard guide](https://docs.stripe.com/dashboard/basics): notifications and actions appear alongside analytics, while filtering lives in the detailed list. LabPulse should put the active faults next to a concise status summary.

## System benchmarks

- [Radix color scale uses](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale): background, border, interactive, and text roles have distinct levels. LabPulse needs role-based colors, not one accent used everywhere.
- [Carbon typography](https://v10.carbondesignsystem.com/guidelines/typography/overview/): product typography stays compact while expressive type is reserved for larger statements. LabPulse can use a strong page title without making every table row dramatic.

## Motion

- [Material duration and easing](https://m1.material.io/motion/duration-easing.html): desktop state changes should finish quickly, around 150–200 ms. LabPulse can use a short modal and filter transition without delaying work.
- [Motion transitions](https://motion.dev/docs/react-transitions): a damped spring settles without a conspicuous bounce. That suits an incident drawer if one is added later; the first version can stay with CSS transitions.

## Typography

- [IBM Plex source](https://github.com/IBM/plex): Plex Sans and Mono are from the same open font family. Sans can carry prose while Mono makes equipment codes and timestamps align.
- [IBM Plex introduction](https://www.ibm.com/plex/): the family was designed for both technical and human contexts. That matches a lab tool used by staff and students.

The category convention worth keeping is a searchable equipment list with explicit status. The convention to break is a wall of generic KPI cards before the user sees a broken instrument. The details to carry forward are readable equipment IDs, restrained status color, and an immediate route from an alert to its asset.
