import React, { useState, useEffect } from 'react';
import {
  Plus, MapPin, Users, Wrench, Book, Heart,
  Search, Factory, Mountain,
} from 'lucide-react';

/**
 * CommunityAssetMapper
 *
 * The human-facing layer of the resilience toolkit.  While the Python
 * modules compute system designs, this component lets a community
 * actually map and share what they have: skills, knowledge, tools,
 * natural resources, local industry, and mutual support.
 *
 * Categories:
 *   - Skills & Abilities (repair, teaching, trade skills)
 *   - Knowledge & Wisdom (traditional medicine, elder knowledge)
 *   - Tools & Equipment (shared tools, workshop access)
 *   - Care & Support (childcare circles, elder care, emergency aid)
 *   - Community Building (gatherings, organizing, conflict resolution)
 *   - Local Industry (machine shops, woodworking, manufacturing)
 *   - Natural Resources (water sources, clay deposits, timber, stone)
 *
 * Each asset includes location, availability, contact method, tags,
 * and category-specific fields (capacity for industry, quantity and
 * access notes for natural resources).
 */
const CommunityAssetMapper = () => {
  const [assets, setAssets] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = {
    skills: {
      icon: Wrench,
      label: 'Skills & Abilities',
      color: 'bg-blue-100 text-blue-800',
    },
    knowledge: {
      icon: Book,
      label: 'Knowledge & Wisdom',
      color: 'bg-green-100 text-green-800',
    },
    resources: {
      icon: MapPin,
      label: 'Tools & Equipment',
      color: 'bg-purple-100 text-purple-800',
    },
    support: {
      icon: Heart,
      label: 'Care & Support',
      color: 'bg-red-100 text-red-800',
    },
    community: {
      icon: Users,
      label: 'Community Building',
      color: 'bg-yellow-100 text-yellow-800',
    },
    industry: {
      icon: Factory,
      label: 'Local Industry & Manufacturing',
      color: 'bg-orange-100 text-orange-800',
    },
    naturalResources: {
      icon: Mountain,
      label: 'Natural Resources',
      color: 'bg-emerald-100 text-emerald-800',
    },
  };

  const emptyAsset = {
    title: '',
    description: '',
    category: 'skills',
    availability: '',
    contact: '',
    location: '',
    tags: '',
    capacity: '',
    quantity: '',
    access: '',
  };

  const [newAsset, setNewAsset] = useState({ ...emptyAsset });

  // Sample data showing the range of community assets
  useEffect(() => {
    setAssets([
      {
        id: 1,
        title: 'Medicinal Plant Knowledge',
        description:
          'Traditional plant medicine, foraging, and healing practices passed down through generations',
        category: 'knowledge',
        availability: 'Weekends, by arrangement',
        contact: 'Message through community board',
        location: 'Near community garden',
        tags: 'healing, plants, traditional, wellness',
        contributor: 'Elder Mary',
      },
      {
        id: 2,
        title: 'Bicycle Repair Tools & Skills',
        description: 'Complete bike repair setup + teaching basic maintenance',
        category: 'skills',
        availability: 'Evenings after 6pm',
        contact: 'Text 555-BIKE',
        location: '3rd Street garage',
        tags: 'transportation, repair, teaching',
        contributor: 'Sam',
      },
      {
        id: 3,
        title: 'Community Garden Space',
        description:
          '1/4 acre plot available for shared growing, tools included',
        category: 'resources',
        availability: 'Always available',
        contact: 'gardengroup@local.net',
        location: 'Behind the library',
        tags: 'food, growing, sharing, sustainability',
        contributor: 'Garden Collective',
      },
      {
        id: 4,
        title: 'Childcare Circle',
        description:
          'Parents taking turns watching each others kids, emergency backup available',
        category: 'support',
        availability: 'Flexible scheduling',
        contact: 'Join our group chat',
        location: 'Various homes',
        tags: 'children, support, cooperation',
        contributor: 'Parent Network',
      },
      {
        id: 5,
        title: 'Local Machine Shop',
        description:
          'Small precision machining operation - can fabricate metal parts, repair equipment, custom tooling',
        category: 'industry',
        availability: 'Mon-Fri, custom orders by arrangement',
        contact: 'MetalWorks Local - 555-METAL',
        location: 'Industrial district, 5th Ave',
        tags: 'manufacturing, metal, repair, custom, precision',
        capacity: 'Small batch custom work, precision to 0.001in',
        contributor: 'MetalWorks',
      },
      {
        id: 6,
        title: 'Artesian Well Access',
        description:
          'Clean groundwater source, historically reliable, community access point established',
        category: 'naturalResources',
        availability: 'Always available',
        contact: 'Well Steward Committee',
        location: 'Behind old schoolhouse',
        tags: 'water, groundwater, emergency, clean, reliable',
        quantity: '500 gallons/hour, tested annually',
        access: 'Community access point, bring own containers',
        contributor: 'Community Well Committee',
      },
      {
        id: 7,
        title: 'Local Pottery Clay Deposits',
        description:
          'High-quality clay suitable for ceramics, building materials, traditional crafts',
        category: 'naturalResources',
        availability: 'Seasonal access - dry months only',
        contact: 'Through indigenous knowledge keeper',
        location: 'East creek bed area',
        tags: 'clay, pottery, building, traditional, seasonal',
        quantity: 'Large deposit, high quality',
        access: 'Permission needed, environmental protocols observed',
        contributor: 'Traditional Crafters',
      },
      {
        id: 8,
        title: 'Community Woodworking Shop',
        description:
          'Furniture making, cabinetry, custom millwork. Training available for basic woodworking',
        category: 'industry',
        availability: 'Wed-Sat, classes on weekends',
        contact: 'WoodCraft Collective',
        location: 'Converted warehouse, Main St',
        tags: 'woodworking, furniture, training, custom, local',
        capacity: 'Full workshop, 6 stations, classes of 8',
        contributor: 'WoodCraft Collective',
      },
    ]);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setAssets([...assets, { ...newAsset, id: Date.now(), contributor: 'You' }]);
    setNewAsset({ ...emptyAsset });
    setShowForm(false);
  };

  const filteredAssets = assets.filter((asset) => {
    const term = searchTerm.toLowerCase();
    const matchesSearch =
      asset.title.toLowerCase().includes(term) ||
      asset.description.toLowerCase().includes(term) ||
      asset.tags.toLowerCase().includes(term);
    const matchesCategory =
      selectedCategory === 'all' || asset.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const AssetCard = ({ asset }) => {
    const category = categories[asset.category];
    const Icon = category.icon;

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Icon className="h-5 w-5 text-gray-600" />
            <span
              className={`px-2 py-1 rounded-full text-xs font-medium ${category.color}`}
            >
              {category.label}
            </span>
          </div>
        </div>

        <h3 className="font-semibold text-gray-900 mb-2">{asset.title}</h3>
        <p className="text-gray-600 text-sm mb-3">{asset.description}</p>

        <div className="space-y-1 text-sm text-gray-500">
          {asset.location && (
            <div>
              <strong>Where:</strong> {asset.location}
            </div>
          )}
          {asset.availability && (
            <div>
              <strong>When:</strong> {asset.availability}
            </div>
          )}
          {asset.contact && (
            <div>
              <strong>Contact:</strong> {asset.contact}
            </div>
          )}
          {asset.category === 'industry' && asset.capacity && (
            <div>
              <strong>Capacity:</strong> {asset.capacity}
            </div>
          )}
          {asset.category === 'naturalResources' && asset.quantity && (
            <div>
              <strong>Estimated Quantity:</strong> {asset.quantity}
            </div>
          )}
          {asset.category === 'naturalResources' && asset.access && (
            <div>
              <strong>Access Notes:</strong> {asset.access}
            </div>
          )}
        </div>

        {asset.tags && (
          <div className="mt-3 flex flex-wrap gap-1">
            {asset.tags.split(',').map((tag, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
              >
                {tag.trim()}
              </span>
            ))}
          </div>
        )}

        <div className="mt-3 text-xs text-gray-400">
          Shared by {asset.contributor}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-gray-50 min-h-screen">
      {/* Header and search */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Community Asset Map
        </h1>
        <p className="text-gray-600 mb-4">
          Discover and share the wealth of resources, skills, and knowledge in
          our community. Building resilience through connection and mutual aid.
        </p>

        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search assets, skills, resources..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <select
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            {Object.entries(categories).map(([key, cat]) => (
              <option key={key} value={key}>
                {cat.label}
              </option>
            ))}
          </select>

          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <Plus className="h-4 w-4" />
            <span>Share an Asset</span>
          </button>
        </div>
      </div>

      {/* New asset form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-lg shadow-sm p-6 mb-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Share a Community Asset
          </h2>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What are you sharing?
                </label>
                <input
                  type="text"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.title}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, title: e.target.value })
                  }
                  placeholder="e.g., Woodworking skills, Garden tools, Elder care"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.category}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, category: e.target.value })
                  }
                >
                  {Object.entries(categories).map(([key, cat]) => (
                    <option key={key} value={key}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                required
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={newAsset.description}
                onChange={(e) =>
                  setNewAsset({ ...newAsset, description: e.target.value })
                }
                placeholder="Describe what you're offering and how it might help others..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Availability
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.availability}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, availability: e.target.value })
                  }
                  placeholder="When is this available?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  General Location
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.location}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, location: e.target.value })
                  }
                  placeholder="Neighborhood/area (keep it general)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Method
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.contact}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, contact: e.target.value })
                  }
                  placeholder="How should people reach you?"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value={newAsset.tags}
                onChange={(e) =>
                  setNewAsset({ ...newAsset, tags: e.target.value })
                }
                placeholder="e.g., repair, teaching, emergency, seasonal"
              />
            </div>

            {/* Industry-specific fields */}
            {newAsset.category === 'industry' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Production Capacity / Capabilities
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={newAsset.capacity}
                  onChange={(e) =>
                    setNewAsset({ ...newAsset, capacity: e.target.value })
                  }
                  placeholder="e.g., Small batch custom work, 50 units/day, precision to 0.001in"
                />
              </div>
            )}

            {/* Natural resources-specific fields */}
            {newAsset.category === 'naturalResources' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Estimated Quantity / Quality
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={newAsset.quantity}
                    onChange={(e) =>
                      setNewAsset({ ...newAsset, quantity: e.target.value })
                    }
                    placeholder="e.g., Abundant, High quality, 500 gallons/hour"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Access Considerations
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    value={newAsset.access}
                    onChange={(e) =>
                      setNewAsset({ ...newAsset, access: e.target.value })
                    }
                    placeholder="e.g., Permission needed, Seasonal access only, Environmental protocols"
                  />
                </div>
              </>
            )}

            <div className="flex space-x-4">
              <button
                type="submit"
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
              >
                Share This Asset
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Asset count */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Community Assets ({filteredAssets.length})
        </h2>
      </div>

      {/* Asset grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAssets.map((asset) => (
          <AssetCard key={asset.id} asset={asset} />
        ))}
      </div>

      {/* Empty state */}
      {filteredAssets.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No assets found
          </h3>
          <p className="text-gray-600">
            {searchTerm || selectedCategory !== 'all'
              ? 'Try adjusting your search or category filter.'
              : 'Be the first to share a community asset!'}
          </p>
        </div>
      )}
    </div>
  );
};

export default CommunityAssetMapper;
