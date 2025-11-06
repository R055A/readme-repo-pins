<!-- START: REPO-PINS -->
# GitHub Profile Repository Pins

Personalize selection, visualization and dynamic ordering of repository pins for public and private GitHub profiles.  
No PAT required, just copy the repo using the template feature for efficient data fetching and visualization rendering.  
Supports multi-language displaying of private and public repository pins for both user and organisation profiles.  
Supports profile website deployment for full utilization of the frequently updated repository pin visualization features.  
Pins can be customized by repo selection, dynamic order, background image (URL or path), and available themes.

![example-1](https://raw.githubusercontent.com/R055A/R055A/refs/heads/main/imgs/0.svg) 
![example-2](https://raw.githubusercontent.com/R055A/R055A/refs/heads/main/imgs/1.svg)

## Instructions

* Simply create a copy of the template repository by clicking [here](https://github.com/new?template_name=readme-repo-pins&template_owner=profile-icons)
  * name the new repository `Repository name*` identical to the `owner*` name.
  * select the green `Create Repository` button.

This creates a GitHub profile with frequently updated repo pins using CI automation and a placeholder:

```
<!-- START: REPO-PINS -->
<!-- END: REPO-PINS -->
```

The text in this repository is removed so that profiles only display the generated repository pins and other content
added outside the placeholder. There is no further setup requirement for the profile repository and its automation.

> The [template repo](https://github.com/profile-icons/readme-repo-pins) (and generated copies) execute the source code in this repo at runtime.

## Configurations (optional)

The repository project was initially created to streamline the display of generated pin visualizations on a 
private profile `README.md`, but supports broader use cases with optional personalization and elevation of API privileges.

### Theme

The optional `THEME` configuration controls the visual color scheme of the generated SVG pin background, border, text, and icon features.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:
* key: `THEME`
* value (either one of the two formats):
  * `{<owner/repo>: <theme_name>}` - individual pin theme(s)
  * `<theme_name>` - single theme for pin(s)

where:
* `owner/repo` matches the owner/repository names in the URL of a given repository - required `<>`
* `theme_name` matches any key in `files/themes.json` - required `<>`

> If a theme is unavailable, you can add it to `files/themes.json` - refer [here](https://github.com/profile-icons/readme-repo-pins-src/issues/1) for more information.

> The default `THEME` is `github_soft`

### Background Image

The optional `BG_IMG` configuration controls the embedding of select imagery to the background of the generated SVG pin(s).

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:
* key: `BG_IMG`
* value (either one of the three formats):
  * `{<owner/repo>: <img-config-dict>}` - individual pin background image(s)
  * `<img-config-dict>` - single background image for pin(s)
  * `<url/filepath>` - single background image for pin(s)

where:
* `owner/repo` matches the owner/repository names in the URL of a given repository - required `<>`
* `img-config-dict` is any stringified dictionary configuration matching the following format
```
{
    "img": <url/filepath>, 
    "align": [align], 
    "mode": [mode], 
    "opacity": [opacity]
}
```
* `url/filepath` is either an image URL or the path to an image file uploaded (to an owned repo) - required `<>`
* `align` is any align keyword value in [preserveAspectRatio](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/preserveAspectRatio#syntax) attribute - optional `[]` (default `xMidYMid`)
* `mode` is any [CSS object-fit](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/object-fit) property value in `[cover, contain, stretch]` - optional `[]` (default `stretch`)
* `opacity` is a float value between `0` and `1.0` - optional `[]` (default `0.25`)

> The default `BG_IMG` is `None` (which defaults to the `THEME` background color)

### Repository List

The optional `REPO_NAMES_EXCLUSIVE` configuration controls the exclusive generation of pins for a given list of repository names.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `REPO_NAMES_EXCLUSIVE`
* value: `<owner/repo>,...,<owner/repo>`

where:
* `owner/repo` matches the owner/repository names in the URL of a given repository - required `<>`
* `<owner/repo>,...,<owner/repo>` is a list of any number of `owner/repo` separated by commas `,`

### API Token

The optional `GH_API_TOKEN` configuration is for elevating GitHub GraphQL API privileges with a [personal access token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
The default [rate limit](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api) when not using a GitHub PAT is 1000 query points per hour and is limited to public repository data. 
The rate limit when using a PAT is increased to 5000, and provides access to authorized private repository data so that pins can be generated for both
public and private repositories to both public and private profiles.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `GH_API_TOKEN`
* value: `[PAT]`

where:
* `PAT` is a GitHub personal access token and can be generated [here](https://github.com/settings/tokens) - optional `[]`

> The default `GH_API_TOKEN` is `GITHUB_TOKEN` (1000 GraphQL API query points per hour)

> A `PAT` is required for displaying private repository pins

### Number

The optional `NUM_REPO_PINS` configuration controls the maximum possible number of repository pins to generate up to a hard limit of `20`.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `NUM_REPO_PINS`
* value: `[num]`

where:
* `num` is any int value greater than `0` - optional `[]`

> The default `NUM_REPO_PINS` is `6`

> Overruled by the `REPO_NAMES_EXCLUSIVE` configuration when default, or the minimum value between both when also set.

### Order

The optional `REPO_PIN_ORDER` configuration controls the dynamic ordering of generated repository pin visualizations.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `REPO_PIN_ORDER`
* value: `[order]`

where:
* `order` is any value in [RepositoryOrderField](https://docs.github.com/en/graphql/reference/enums#repositoryorderfield) - optional `[]`

> The default `REPO_PIN_ORDER` is `STARGAZERS`

> Overruled by the `REPO_NAMES_EXCLUSIVE` configuration when default, but not when also set.

### Exclude Owned Repositories (Not Pinned)

By default, repository data collected for generating pin visualizations is first those pinned by a user, followed by
other repositories owned by the user, and then other repositories the user has contributed to but does not own.

The optional `IS_EXCLUDE_REPOS_OWNED` configuration controls whether repositories owned by a user but not pinned are excluded.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `IS_EXCLUDE_REPOS_OWNED`
* value: `[is_exclude]`

where:
* `is_exclude` is either `true` or `false` (or empty to represent false) - optional `[]`

> The default `IS_EXCLUDE_REPOS_OWNED` is `false`

> Overruled by the `REPO_NAMES_EXCLUSIVE` configuration, as pin visuals are generated only for listed repositories.

### Exclude Contributed Repositories (Neither Owned Nor Pinned)

By default, repository data collected for generating pin visualizations is first those pinned by a user, followed by
other repositories owned by the user, and then other repositories the user has contributed to but does not own.

The optional `IS_EXCLUDE_REPOS_CONTRIBUTED` configuration controls whether repositories contributed to but not owned by a user are excluded.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `IS_EXCLUDE_REPOS_CONTRIBUTED`
* value: `[is_exclude]`

where:
* `is_exclude` is either `true` or `false` (or empty to represent false) - optional `[]`

> The default `IS_EXCLUDE_REPOS_CONTRIBUTED` is `false`

> Overruled by the `REPO_NAMES_EXCLUSIVE` configuration, as pin visuals are generated only for listed repositories.

### Username

The optional `GH_USERNAME` configuration controls which (pinned/owned/contributed to) repositories are displayed by association.

This can be set by creating a [GitHub Action](https://docs.github.com/en/actions) (in a template-generated repo) with the following key-value field pairs:

* key: `GH_USERNAME`
* value: `[username]`

where:
* `username` must match the username associated with repositories pinned/owned/contributed to by the user the pin display focuses on - optional `[]`

> The default `GH_USERNAME` is `github.repository_owner` (the username associated with the owner of the template-generated repo)

> `GH_USERNAME` is required for displaying pins on an organisation profile

<!-- END: REPO-PINS -->
