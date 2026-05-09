use std::collections::HashSet;

use anyhow::anyhow;
use serde::{Deserialize, Serialize};

// ── Controlled-vocabulary enums ───────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RawCause {
    Poisoned,
    Shot,
    Stabbed,
    Clubbed,
    Strangled,
    Drowned,
    Burned,
    Hanged,
    Fell,
    Crushed,
    Suffocated,
    Exploded,
    Electrocuted,
    Frozen,
    Illness,
    Eaten,
    TornApart,
    Vehicular,
    Unstated,
    Other,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RawDeathType {
    Homicide,
    AttemptedHomicide,
    Execution,
    Accident,
    NaturalDeath,
    Unstated,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Motive {
    GreedInheritance,
    GreedFinancial,
    Blackmail,
    Jealousy,
    Revenge,
    Ideology,
    SelfDefense,
    Concealment,
    Passion,
    VigilanteJustice,
    Freedom,
    FamilyProtection,
    Pathological,
    Mercy,
    Penance,
    Unstated,
    Other,
    NeedsReview,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MensRea {
    Purposely,
    Knowingly,
    Recklessly,
    Negligently,
    Accidentally,
    Unstated,
    NeedsReview,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum KillerCircumstance {
    Justified,
    Mitigated,
    Neutral,
    Unstated,
    NeedsReview,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum MysteryTrope {
    LockedRoom,
    ImpossibleCrime,
    HowCatchem,
    Whodunit,
    Whydunit,
    Howdunit,
    DyingClue,
    AlibiTrick,
    ClosedCircle,
    NeedleInHaystack,
    LeastLikelySuspect,
    FrameUp,
    MistakenIdentity,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RoleInStory {
    Protagonist,
    Antagonist,
    Victim,
    Detective,
    Bystander,
    Unstated,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum MediaType {
    Book,
    Movie,
    TvShow,
    TvEpisode,
    Game,
    ShortStory,
    Play,
    Podcast,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ExternalPageStatus {
    Exists,
    None,
    NeedsReview,
}

impl Default for ExternalPageStatus {
    fn default() -> Self {
        Self::NeedsReview
    }
}

// ── Domain enums (invalid states unrepresentable) ────────────────────────────

/// Cause of death. All variants except `Other` carry a mandatory `means` field
/// describing the specific weapon, substance, or mechanism.
#[derive(Debug, Clone)]
pub enum Cause {
    Poisoned { means: String },
    Shot { means: String },
    Stabbed { means: String },
    Clubbed { means: String },
    Strangled { means: String },
    Drowned { means: String },
    Burned { means: String },
    Hanged { means: String },
    Fell { means: String },
    Crushed { means: String },
    Suffocated { means: String },
    Exploded { means: String },
    Electrocuted { means: String },
    Frozen { means: String },
    Illness { means: String },
    Eaten { means: String },
    TornApart { means: String },
    Vehicular { means: String },
    Unstated { means: String },
    Other,
}

/// Death classification. `Accident` and `NaturalDeath` carry no motive;
/// all other variants require one. Suicide is represented as `Homicide`
/// with the victim also listed as a killer.
#[derive(Debug, Clone)]
pub enum DeathType {
    Homicide { motive: Motive, motive_detail: Option<String> },
    AttemptedHomicide { motive: Motive, motive_detail: Option<String> },
    Execution { motive: Motive, motive_detail: Option<String> },
    Unstated { motive: Motive, motive_detail: Option<String> },
    Accident,
    NaturalDeath,
}

// ── Wire types (flat JSON, one-to-one with stored format) ────────────────────

#[derive(Debug, Deserialize, Serialize)]
pub struct DeathWire {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub victim_id: Option<String>,
    #[serde(skip_serializing, default)]
    pub victim_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ordinal: Option<u32>,
    pub cause: RawCause,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub means: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub cause_detail: Option<String>,
    pub death_type: RawDeathType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub motive: Option<Motive>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub motive_detail: Option<String>,
    #[serde(default)]
    pub killers: Vec<Killer>,
    #[serde(default)]
    pub tropes: Vec<MysteryTrope>,
    #[serde(default)]
    pub is_central_death: bool,
    #[serde(default)]
    pub is_twist: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub chapter_or_act: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MediaItemWire {
    pub slug: Option<String>,
    pub wikidata_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tmdb_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub igdb_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub isbn: Option<String>,
    pub title: String,
    pub media_type: MediaType,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub year: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub creator: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub series_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub series_number: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    #[serde(default)]
    pub tags: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub external_links: Option<ExternalLinks>,
    #[serde(default)]
    pub persons: Vec<Person>,
    #[serde(default)]
    pub deaths: Vec<Death>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub episodes: Vec<TvEpisode>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub cases: Vec<GameCase>,
}

// ── Simple domain structs (no cross-field constraints) ───────────────────────

fn default_true() -> bool {
    true
}

pub(crate) fn slugify(s: &str) -> String {
    s.to_lowercase()
        .chars()
        .map(|c| if c.is_alphanumeric() { c } else { '-' })
        .collect::<String>()
        .split('-')
        .filter(|seg| !seg.is_empty())
        .collect::<Vec<_>>()
        .join("-")
}

pub(crate) fn assign_person_ids(persons: &mut [Person]) {
    let mut used: HashSet<String> = persons.iter().filter_map(|p| p.id.clone()).collect();
    for p in persons.iter_mut() {
        if p.id.is_none() {
            let base = slugify(&p.name);
            let id = if !used.contains(&base) {
                base.clone()
            } else {
                let mut n = 2u32;
                loop {
                    let candidate = format!("{base}-{n}");
                    if !used.contains(&candidate) {
                        break candidate;
                    }
                    n += 1;
                }
            };
            used.insert(id.clone());
            p.id = Some(id);
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Killer {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub person_id: Option<String>,
    #[serde(skip_serializing, default)]
    pub name: Option<String>,
    pub mens_rea: MensRea,
    pub circumstance: KillerCircumstance,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Person {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,
    pub name: String,
    #[serde(default = "default_true")]
    pub is_fictional: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub role_in_story: Option<RoleInStory>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub is_solver: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub nationality: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub ethnicity: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gender: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub approximate_age: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub profession: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub skills: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub archetype: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ExternalLinks {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tvtropes_slug: Option<String>,
    #[serde(default)]
    pub tvtropes_status: ExternalPageStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wikipedia_slug: Option<String>,
    #[serde(default)]
    pub wikipedia_status: ExternalPageStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fandom_slug: Option<String>,
    #[serde(default)]
    pub fandom_status: ExternalPageStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub goodreads_id: Option<String>,
    #[serde(default)]
    pub goodreads_status: ExternalPageStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub steam_id: Option<String>,
    #[serde(default)]
    pub steam_status: ExternalPageStatus,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub itch_slug: Option<String>,
    #[serde(default)]
    pub itch_status: ExternalPageStatus,
}

impl ExternalLinks {
    pub fn normalize(&mut self) {
        if self.tvtropes_slug.is_some() {
            self.tvtropes_status = ExternalPageStatus::Exists;
        }
        if self.wikipedia_slug.is_some() {
            self.wikipedia_status = ExternalPageStatus::Exists;
        }
        if self.fandom_slug.is_some() {
            self.fandom_status = ExternalPageStatus::Exists;
        }
        if self.goodreads_id.is_some() {
            self.goodreads_status = ExternalPageStatus::Exists;
        }
        if self.steam_id.is_some() {
            self.steam_status = ExternalPageStatus::Exists;
        }
        if self.itch_slug.is_some() {
            self.itch_status = ExternalPageStatus::Exists;
        }
    }
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct TvEpisode {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub wikidata_id: Option<String>,
    pub title: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub season: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub episode_number: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub year: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    #[serde(default)]
    pub tags: Vec<String>,
    #[serde(default)]
    pub persons: Vec<Person>,
    #[serde(default)]
    pub deaths: Vec<Death>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct GameCase {
    pub title: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub case_number: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    #[serde(default)]
    pub tags: Vec<String>,
    #[serde(default)]
    pub persons: Vec<Person>,
    #[serde(default)]
    pub deaths: Vec<Death>,
}

// ── Death (wire ↔ domain) ─────────────────────────────────────────────────────

/// Fully validated death event. `cause` and `death_type` enforce their
/// required fields at the type level — no runtime checks needed for those.
/// `victim_name` is a carry-through from the wire format for name→ID resolution
/// in `MediaItem::try_from`; it is never serialised.
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(try_from = "DeathWire", into = "DeathWire")]
pub struct Death {
    pub victim_id: Option<String>,
    pub victim_name: Option<String>,
    pub ordinal: Option<u32>,
    pub cause: Cause,
    pub cause_detail: Option<String>,
    pub death_type: DeathType,
    pub killers: Vec<Killer>,
    pub tropes: Vec<MysteryTrope>,
    pub is_central_death: bool,
    pub is_twist: bool,
    pub chapter_or_act: Option<String>,
    pub notes: Option<String>,
}

impl TryFrom<DeathWire> for Death {
    type Error = anyhow::Error;

    fn try_from(w: DeathWire) -> Result<Self, Self::Error> {
        let needs_means = |means: Option<String>, label: &'static str| {
            means.ok_or_else(|| anyhow!("`means` is required when cause is {label}"))
        };

        let cause = match w.cause {
            RawCause::Poisoned => Cause::Poisoned { means: needs_means(w.means, "POISONED")? },
            RawCause::Shot => Cause::Shot { means: needs_means(w.means, "SHOT")? },
            RawCause::Stabbed => Cause::Stabbed { means: needs_means(w.means, "STABBED")? },
            RawCause::Clubbed => Cause::Clubbed { means: needs_means(w.means, "CLUBBED")? },
            RawCause::Strangled => Cause::Strangled { means: needs_means(w.means, "STRANGLED")? },
            RawCause::Drowned => Cause::Drowned { means: needs_means(w.means, "DROWNED")? },
            RawCause::Burned => Cause::Burned { means: needs_means(w.means, "BURNED")? },
            RawCause::Hanged => Cause::Hanged { means: needs_means(w.means, "HANGED")? },
            RawCause::Fell => Cause::Fell { means: needs_means(w.means, "FELL")? },
            RawCause::Crushed => Cause::Crushed { means: needs_means(w.means, "CRUSHED")? },
            RawCause::Suffocated => Cause::Suffocated { means: needs_means(w.means, "SUFFOCATED")? },
            RawCause::Exploded => Cause::Exploded { means: needs_means(w.means, "EXPLODED")? },
            RawCause::Electrocuted => Cause::Electrocuted { means: needs_means(w.means, "ELECTROCUTED")? },
            RawCause::Frozen => Cause::Frozen { means: needs_means(w.means, "FROZEN")? },
            RawCause::Illness => Cause::Illness { means: needs_means(w.means, "ILLNESS")? },
            RawCause::Eaten => Cause::Eaten { means: needs_means(w.means, "EATEN")? },
            RawCause::TornApart => Cause::TornApart { means: needs_means(w.means, "TORN_APART")? },
            RawCause::Vehicular => Cause::Vehicular { means: needs_means(w.means, "VEHICULAR")? },
            RawCause::Unstated => Cause::Unstated { means: needs_means(w.means, "UNSTATED")? },
            RawCause::Other => Cause::Other,
        };

        let needs_motive = |motive: Option<Motive>, label: &'static str| {
            motive.ok_or_else(|| anyhow!("`motive` is required when death_type is {label}"))
        };

        let death_type = match w.death_type {
            RawDeathType::Homicide => DeathType::Homicide {
                motive: needs_motive(w.motive, "homicide")?,
                motive_detail: w.motive_detail,
            },
            RawDeathType::AttemptedHomicide => DeathType::AttemptedHomicide {
                motive: needs_motive(w.motive, "attempted_homicide")?,
                motive_detail: w.motive_detail,
            },
            RawDeathType::Execution => DeathType::Execution {
                motive: needs_motive(w.motive, "execution")?,
                motive_detail: w.motive_detail,
            },
            RawDeathType::Unstated => DeathType::Unstated {
                motive: needs_motive(w.motive, "unstated")?,
                motive_detail: w.motive_detail,
            },
            RawDeathType::Accident => DeathType::Accident,
            RawDeathType::NaturalDeath => DeathType::NaturalDeath,
        };

        Ok(Death {
            victim_id: w.victim_id,
            victim_name: w.victim_name,
            ordinal: w.ordinal,
            cause,
            cause_detail: w.cause_detail,
            death_type,
            killers: w.killers,
            tropes: w.tropes,
            is_central_death: w.is_central_death,
            is_twist: w.is_twist,
            chapter_or_act: w.chapter_or_act,
            notes: w.notes,
        })
    }
}

impl From<Death> for DeathWire {
    fn from(d: Death) -> Self {
        let (cause, means) = match d.cause {
            Cause::Poisoned { means } => (RawCause::Poisoned, Some(means)),
            Cause::Shot { means } => (RawCause::Shot, Some(means)),
            Cause::Stabbed { means } => (RawCause::Stabbed, Some(means)),
            Cause::Clubbed { means } => (RawCause::Clubbed, Some(means)),
            Cause::Strangled { means } => (RawCause::Strangled, Some(means)),
            Cause::Drowned { means } => (RawCause::Drowned, Some(means)),
            Cause::Burned { means } => (RawCause::Burned, Some(means)),
            Cause::Hanged { means } => (RawCause::Hanged, Some(means)),
            Cause::Fell { means } => (RawCause::Fell, Some(means)),
            Cause::Crushed { means } => (RawCause::Crushed, Some(means)),
            Cause::Suffocated { means } => (RawCause::Suffocated, Some(means)),
            Cause::Exploded { means } => (RawCause::Exploded, Some(means)),
            Cause::Electrocuted { means } => (RawCause::Electrocuted, Some(means)),
            Cause::Frozen { means } => (RawCause::Frozen, Some(means)),
            Cause::Illness { means } => (RawCause::Illness, Some(means)),
            Cause::Eaten { means } => (RawCause::Eaten, Some(means)),
            Cause::TornApart { means } => (RawCause::TornApart, Some(means)),
            Cause::Vehicular { means } => (RawCause::Vehicular, Some(means)),
            Cause::Unstated { means } => (RawCause::Unstated, Some(means)),
            Cause::Other => (RawCause::Other, None),
        };

        let (death_type, motive, motive_detail) = match d.death_type {
            DeathType::Homicide { motive, motive_detail } => {
                (RawDeathType::Homicide, Some(motive), motive_detail)
            }
            DeathType::AttemptedHomicide { motive, motive_detail } => {
                (RawDeathType::AttemptedHomicide, Some(motive), motive_detail)
            }
            DeathType::Execution { motive, motive_detail } => {
                (RawDeathType::Execution, Some(motive), motive_detail)
            }
            DeathType::Unstated { motive, motive_detail } => {
                (RawDeathType::Unstated, Some(motive), motive_detail)
            }
            DeathType::Accident => (RawDeathType::Accident, None, None),
            DeathType::NaturalDeath => (RawDeathType::NaturalDeath, None, None),
        };

        DeathWire {
            victim_id: d.victim_id,
            victim_name: None,
            ordinal: d.ordinal,
            cause,
            means,
            cause_detail: d.cause_detail,
            death_type,
            motive,
            motive_detail,
            killers: d.killers,
            tropes: d.tropes,
            is_central_death: d.is_central_death,
            is_twist: d.is_twist,
            chapter_or_act: d.chapter_or_act,
            notes: d.notes,
        }
    }
}

// ── MediaItem (wire ↔ domain) ─────────────────────────────────────────────────

/// Resolves any `victim_name`/`killer.name` carry-throughs to person IDs.
/// Must run after `assign_person_ids` so every person already has an ID.
pub(crate) fn resolve_death_refs(
    persons: &[Person],
    deaths: &mut [Death],
    context: &str,
) -> anyhow::Result<()> {
    let name_to_id: std::collections::HashMap<&str, &str> = persons
        .iter()
        .filter_map(|p| p.id.as_deref().map(|id| (p.name.as_str(), id)))
        .collect();

    for death in deaths.iter_mut() {
        if death.victim_id.is_none() {
            if let Some(name) = death.victim_name.take() {
                let id = name_to_id.get(name.as_str()).ok_or_else(|| {
                    anyhow!("victim_name '{}' not in persons for '{}'", name, context)
                })?;
                death.victim_id = Some(id.to_string());
            }
        }
        for killer in death.killers.iter_mut() {
            if killer.person_id.is_none() {
                if let Some(name) = killer.name.take() {
                    let id = name_to_id.get(name.as_str()).ok_or_else(|| {
                        anyhow!("killer '{}' not in persons for '{}'", name, context)
                    })?;
                    killer.person_id = Some(id.to_string());
                } else {
                    anyhow::bail!("killer missing both person_id and name in '{}'", context);
                }
            }
        }
    }
    Ok(())
}

pub(crate) fn validate_death_refs(
    persons: &[Person],
    deaths: &[Death],
    context: &str,
) -> anyhow::Result<()> {
    let known: HashSet<&str> = persons.iter().filter_map(|p| p.id.as_deref()).collect();
    for death in deaths {
        if let Some(vid) = &death.victim_id {
            if !known.contains(vid.as_str()) {
                anyhow::bail!("victim_id '{}' not in persons for '{}'", vid, context);
            }
        }
        for killer in &death.killers {
            match &killer.person_id {
                Some(pid) if known.contains(pid.as_str()) => {}
                Some(pid) => anyhow::bail!(
                    "killer person_id '{}' not in persons for '{}'",
                    pid,
                    context
                ),
                None => anyhow::bail!("killer has no person_id in '{}'", context),
            }
        }
    }
    Ok(())
}

/// Fully validated media item. `slug` is always populated (from `wikidata_id`
/// if not supplied explicitly). Death references are checked against the
/// `persons` list of the enclosing scope.
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(try_from = "MediaItemWire", into = "MediaItemWire")]
pub struct MediaItem {
    pub slug: String,
    pub wikidata_id: Option<String>,
    pub tmdb_id: Option<String>,
    pub igdb_id: Option<String>,
    pub isbn: Option<String>,
    pub title: String,
    pub media_type: MediaType,
    pub year: Option<u32>,
    pub creator: Option<String>,
    pub series_name: Option<String>,
    pub series_number: Option<f64>,
    pub notes: Option<String>,
    pub tags: Vec<String>,
    pub external_links: Option<ExternalLinks>,
    pub persons: Vec<Person>,
    pub deaths: Vec<Death>,
    pub episodes: Vec<TvEpisode>,
    pub cases: Vec<GameCase>,
}

impl TryFrom<MediaItemWire> for MediaItem {
    type Error = anyhow::Error;

    fn try_from(mut w: MediaItemWire) -> Result<Self, Self::Error> {
        let slug = w
            .slug
            .take()
            .or_else(|| w.wikidata_id.clone())
            .ok_or_else(|| anyhow!("either `slug` or `wikidata_id` must be provided"))?;

        assign_person_ids(&mut w.persons);
        for ep in &mut w.episodes {
            assign_person_ids(&mut ep.persons);
        }
        for case in &mut w.cases {
            assign_person_ids(&mut case.persons);
        }

        resolve_death_refs(&w.persons, &mut w.deaths, &w.title)?;
        for ep in &mut w.episodes {
            resolve_death_refs(&ep.persons, &mut ep.deaths, &ep.title)?;
        }
        for case in &mut w.cases {
            resolve_death_refs(&case.persons, &mut case.deaths, &case.title)?;
        }

        validate_death_refs(&w.persons, &w.deaths, &w.title)?;
        for ep in &w.episodes {
            validate_death_refs(&ep.persons, &ep.deaths, &ep.title)?;
        }
        for case in &w.cases {
            validate_death_refs(&case.persons, &case.deaths, &case.title)?;
        }

        if let Some(ref mut el) = w.external_links {
            el.normalize();
        }

        Ok(MediaItem {
            slug,
            wikidata_id: w.wikidata_id,
            tmdb_id: w.tmdb_id,
            igdb_id: w.igdb_id,
            isbn: w.isbn,
            title: w.title,
            media_type: w.media_type,
            year: w.year,
            creator: w.creator,
            series_name: w.series_name,
            series_number: w.series_number,
            notes: w.notes,
            tags: w.tags,
            external_links: w.external_links,
            persons: w.persons,
            deaths: w.deaths,
            episodes: w.episodes,
            cases: w.cases,
        })
    }
}

impl From<MediaItem> for MediaItemWire {
    fn from(m: MediaItem) -> Self {
        MediaItemWire {
            slug: Some(m.slug),
            wikidata_id: m.wikidata_id,
            tmdb_id: m.tmdb_id,
            igdb_id: m.igdb_id,
            isbn: m.isbn,
            title: m.title,
            media_type: m.media_type,
            year: m.year,
            creator: m.creator,
            series_name: m.series_name,
            series_number: m.series_number,
            notes: m.notes,
            tags: m.tags,
            external_links: m.external_links,
            persons: m.persons,
            deaths: m.deaths,
            episodes: m.episodes,
            cases: m.cases,
        }
    }
}

// ── SiteData (top-level typed collections) ────────────────────────────────────

/// Top-level container for `public/site_data.json`.
/// Each field holds only items of the matching `media_type`, which makes the
/// schema self-documenting and eliminates conditional field validation.
#[derive(Debug, Default, Serialize, Deserialize)]
pub struct SiteData {
    #[serde(default)]
    pub books: Vec<MediaItemWire>,
    #[serde(default)]
    pub games: Vec<MediaItemWire>,
    #[serde(default)]
    pub movies: Vec<MediaItemWire>,
    #[serde(default)]
    pub tv_episodes: Vec<MediaItemWire>,
    #[serde(default)]
    pub tv_shows: Vec<MediaItemWire>,
    #[serde(default)]
    pub short_stories: Vec<MediaItemWire>,
    #[serde(default)]
    pub plays: Vec<MediaItemWire>,
    #[serde(default)]
    pub podcasts: Vec<MediaItemWire>,
}

impl SiteData {
    pub fn all_items(&self) -> Vec<&MediaItemWire> {
        self.books.iter()
            .chain(self.games.iter())
            .chain(self.movies.iter())
            .chain(self.tv_episodes.iter())
            .chain(self.tv_shows.iter())
            .chain(self.short_stories.iter())
            .chain(self.plays.iter())
            .chain(self.podcasts.iter())
            .collect()
    }

    #[allow(dead_code)]
    pub fn push(&mut self, item: MediaItemWire) {
        match item.media_type {
            MediaType::Book => self.books.push(item),
            MediaType::Game => self.games.push(item),
            MediaType::Movie => self.movies.push(item),
            MediaType::TvEpisode => self.tv_episodes.push(item),
            MediaType::TvShow => self.tv_shows.push(item),
            MediaType::ShortStory => self.short_stories.push(item),
            MediaType::Play => self.plays.push(item),
            MediaType::Podcast => self.podcasts.push(item),
        }
    }
}
