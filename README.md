# smolsaml

[![PyPI - Version](https://img.shields.io/pypi/v/smolsaml.svg)](https://pypi.org/project/smolsaml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/smolsaml.svg)](https://pypi.org/project/smolsaml)
![Codecov](https://img.shields.io/codecov/c/github/akx/smolsaml.svg)

---

A very minimal SAML 2.0 SP implementation for modern Python versions.

## Support

This library is not meant to be a full-featured SAML 2.0 implementation, but to provide a minimal,
robust implementation without too many dependencies.

It has successfully been tested against:

- [Google Workspace SAML](https://support.google.com/a/answer/6087519?hl=en)
- [Keycloak](https://www.keycloak.org/) 12.0.4
- [Okta](https://www.okta.com/)
- [Microsoft Azure AD](https://learn.microsoft.com/en-us/azure/active-directory/fundamentals/auth-saml)
  - Please note that when using the federationmetadata.xml URL for metadata,
    you will need to specify your app's `appid` in the URL in order for Azure
    to supply the correct key material needed to validate the signature.
    IOW, `https://login.microsoftonline.com/TENANTID/federationmetadata/2007-06/federationmetadata.xml?appid=APPID`.
    Eliding the `appid` parameter will make things not work.

## Installation

The package is available on PyPI.

```console
pip install smolsaml
```

In addition, you will need the [`xmlsec`](https://www.aleksey.com/xmlsec/xmlsec-man.html) (aka `xmlsec1`) utility,
as to avoid a dependency on `lxml` and `python-xmlsec` (which can be a pain to install and may conflict with
one another due to `libxml` version requirements).

- On Debian/Ubuntu, this can be installed with `apt install xmlsec1`.
- On macOS, this can be installed with `brew install libxmlsec1`.

## Usage

We'll go ahead and assume you've chosen to use some sort of web framework (the library doesn't care).

The steps to authenticate a user are:

- Construct an `SPConfiguration` that describes your application. The values need to match what you've
  configured in your IdP, and naturally the ACS URL will need to be hooked up somehow in your web framework.
- Construct an `IDPConfiguration`; the easiest way to do this is `IDPConfiguration.from_metadata_xml`.
  (You'll need to have fetched the metadata yourself, the library doesn't care how you do that.)
- Call `initiate_login`; you'll get a `Redirect` object, which describes where you'll want to whisk
  the user off to.
- The user will authenticate with the IdP, and then be redirected back to your ACS URL.
- In your ACS endpoint, read the `SAMLResponse` POST parameter.
  Call `process_saml_response` with it, and your configuration objects. This will raise an exception if the
  data is not valid. If it is valid, you'll get a `SAMLResponse` object back, which contains the user's
  attributes. It probably will be a good idea to try to disallow multiple `SAMLResponse`s with the same ID;
  that sounds like a replay attack.

## Unsupported features, known bugs, etc.

- :point_right: This library hasn't been tested against any IdPs other than the ones listed above.
  If you have a different IdP and it works, please let me know!
- :point_right: This library doesn't support practically any optional SAML 2.0 feature.
- :point_right: Not all claims that should probably be checked are currently checked.
- Authentication request signing is currently not supported. However, happily, most IdPs don't require it.

## License

`smolsaml` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
