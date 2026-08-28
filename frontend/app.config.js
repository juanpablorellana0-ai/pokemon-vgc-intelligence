/**
 * Dynamic Expo config — extends app.json at runtime.
 *
 * Adds the Base44 preview origin to Expo's CORS allowed hosts so the
 * dev server accepts bundle/HMR requests proxied through the preview URL.
 * The preview hostname changes when the environment is recreated, so it
 * is derived from BASE44_PUBLIC_HOST_SUFFIX (never hardcoded).
 */
export default ({ config }) => {
  const suffix = process.env.BASE44_PUBLIC_HOST_SUFFIX;
  if (suffix) {
    const origin = `https://3000-${suffix}`;
    config.extra = {
      ...(config.extra || {}),
      router: {
        ...(config.extra?.router || {}),
        origin,
      },
    };
  }
  return config;
};
